"""
ZCE ON-DEVICE CONTINUAL LEARNING
══════════════════════════════════
The model learns from new data by itself.
No server. No retraining pipeline. No file replacement.

What this adds on top of the base ZCE VM:
  - Backward pass (backpropagation) inside the VM
  - Gradient accumulation in float arrays
  - Weight update via SGD directly on stored weights
  - On-device learning loop: see data → compute loss → update weights

Architecture:
  Forward:  x → W1 → b1 → activation → W2 → b2 → softmax → loss
  Backward: loss → dW2, db2 → dh → dW1, db1
  Update:   W -= lr * dW  (in-place, streamed as FSET)

This runs entirely inside the ZCE Python VM.
No numpy for the learning step. The VM does it.
"""

import math, sys, time, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import (
    GenericVM, encode, decode, BASE_PRIMITIVES,
    make_leaky_relu_1input, make_swish_def, make_elu_1input,
    train_model, export_model,
    eg_enc, eg_dec, tok, ptr, f32_enc, f32_dec,
    FLOAT_INSTR_R, INSTR_R, D_TOP,
)

PASS = '✓ PASS'
FAIL = '✗ FAIL'

def section(title):
    print(f"\n{'═'*65}")
    print(f"  {title}")
    print(f"{'═'*65}\n")


# ══════════════════════════════════════════════════════════════
# EXTENDED VM WITH BACKWARD PASS
# Adds gradient operations to GenericVM
# ══════════════════════════════════════════════════════════════

class LearningVM(GenericVM):
    """
    Extends GenericVM with:
    - MAT_VEC_T: matrix-vector multiply with transpose (for backward pass)
    - OUTER_ADD: outer product accumulate (for weight gradients)
    - VEC_SCALE: scale a vector by a scalar (for learning rate)
    - VEC_SUB:   in-place vector subtraction (for weight update)
    - LEAKY_GRAD: derivative of leaky relu
    - SOFTMAX_GRAD: combined softmax + cross-entropy gradient
    - CROSS_ENTROPY_LOSS: compute scalar loss for monitoring
    """

    def run(self, bitstream, float_slots=None):
        """Override run() to handle new gradient ops."""
        if float_slots is None: float_slots = set()
        ops, data = decode(bitstream, float_slots)
        data = list(data)
        farrays = []
        user_ops_runtime = {}

        def ext(s):
            while s >= len(data): data.append(0)

        def safe_fget(fid, idx):
            if fid < len(farrays) and 0 <= idx < len(farrays[fid]):
                return farrays[fid][idx]
            return 0.0

        def safe_fset(fid, idx, val):
            if fid < len(farrays) and 0 <= idx < len(farrays[fid]):
                farrays[fid][idx] = float(val)

        pc = 0; steps = 0

        while pc < len(ops):
            if steps > self.max_steps: print('  [VM: step limit]'); break
            steps += 1
            op = ops[pc]; name = op['op']; args = op.get('args', [])

            # ── Grammar ops ───────────────────────────────
            if name == 'DEFINE_OP':
                user_ops_runtime[op['op_id']] = op['user_ops'][op['op_id']]

            elif name == 'CALL_OP':
                op_id  = int(data[args[0]])
                x_slot = args[1]; out_slot = args[2]; n_slot = args[3]
                if op_id not in user_ops_runtime:
                    raise ValueError(f"CALL_OP: op_id {op_id} not defined")
                op_def = user_ops_runtime[op_id]
                x_id  = int(data[x_slot]); out_id = int(data[out_slot])
                n     = int(data[n_slot])
                x   = farrays[x_id]   if x_id  < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(x), len(out))):
                    out[i] = self.execute_user_op(op_def, x[i])
                self.ops_executed[op_id] = self.ops_executed.get(op_id, 0) + 1

            # ── Float arrays ───────────────────────────────
            elif name == 'FARR_NEW' and len(args) >= 2:
                ext(args[1]); size = int(data[args[0]]); arr_id = len(farrays)
                farrays.append([0.0] * size); data[args[1]] = arr_id

            elif name == 'FGET' and len(args) >= 3:
                ext(args[2]); arr_id = int(data[args[0]]); idx = int(data[args[1]])
                data[args[2]] = safe_fget(arr_id, idx)

            elif name == 'FSET' and len(args) >= 3:
                arr_id = int(data[args[0]]); idx = int(data[args[1]])
                val = float(data[args[2]]); safe_fset(arr_id, idx, val)

            # ── Forward pass ops ───────────────────────────
            elif name == 'MAT_VEC' and len(args) >= 5:
                W_id  = int(data[args[0]]); x_id  = int(data[args[1]])
                out_id= int(data[args[2]]); rows  = int(data[args[3]])
                cols  = int(data[args[4]])
                W = farrays[W_id] if W_id < len(farrays) else []
                x = farrays[x_id] if x_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(rows, len(out))):
                    s = 0.0
                    for j in range(min(cols, len(x))):
                        if i*cols+j < len(W): s += W[i*cols+j] * x[j]
                    out[i] = s

            elif name == 'VEC_ADD' and len(args) >= 4:
                a_id = int(data[args[0]]); b_id = int(data[args[1]])
                out_id = int(data[args[2]]); n = int(data[args[3]])
                a = farrays[a_id] if a_id < len(farrays) else []
                b = farrays[b_id] if b_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(a), len(b), len(out))):
                    out[i] = a[i] + b[i]

            elif name == 'SOFTMAX_VEC' and len(args) >= 3:
                x_id = int(data[args[0]]); out_id = int(data[args[1]])
                n = int(data[args[2]])
                x = farrays[x_id] if x_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                if x and n > 0:
                    m = max(x[:n])
                    exps = [math.exp(min(xi-m, 88.0)) for xi in x[:n]]
                    s = sum(exps)
                    for i in range(min(n, len(out))):
                        out[i] = exps[i]/s if s else 1.0/n

            elif name == 'ARGMAX' and len(args) >= 3:
                arr_id = int(data[args[0]]); n = int(data[args[1]])
                out_slot = args[2]; ext(out_slot)
                arr = farrays[arr_id] if arr_id < len(farrays) else []
                if arr and n > 0:
                    best = 0
                    for i in range(1, min(n, len(arr))):
                        if arr[i] > arr[best]: best = i
                    data[out_slot] = best
                else: data[out_slot] = 0

            # ── NEW: Backward pass ops ─────────────────────

            elif name == 'MAT_VEC_T' and len(args) >= 5:
                # W^T @ v  (transpose multiply — for backprop through linear layer)
                # args: W_id, v_id, out_id, rows(of W), cols(of W)
                # result shape: cols (= input size)
                W_id  = int(data[args[0]]); v_id  = int(data[args[1]])
                out_id= int(data[args[2]]); rows  = int(data[args[3]])
                cols  = int(data[args[4]])
                W = farrays[W_id] if W_id < len(farrays) else []
                v = farrays[v_id] if v_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                # out[j] = sum_i W[i*cols+j] * v[i]
                for j in range(min(cols, len(out))):
                    s = 0.0
                    for i in range(min(rows, len(v))):
                        if i*cols+j < len(W): s += W[i*cols+j] * v[i]
                    out[j] = s

            elif name == 'OUTER_ADD' and len(args) >= 5:
                # W += scale * outer(a, b)  (gradient accumulation for weights)
                # args: W_id, a_id, b_id, rows, cols, scale_slot
                W_id  = int(data[args[0]]); a_id = int(data[args[1]])
                b_id  = int(data[args[2]]); rows = int(data[args[3]])
                cols  = int(data[args[4]])
                scale = float(data[args[5]]) if len(args) > 5 else 1.0
                W = farrays[W_id] if W_id < len(farrays) else []
                a = farrays[a_id] if a_id < len(farrays) else []
                b = farrays[b_id] if b_id < len(farrays) else []
                for i in range(min(rows, len(a))):
                    for j in range(min(cols, len(b))):
                        if i*cols+j < len(W):
                            W[i*cols+j] += scale * a[i] * b[j]

            elif name == 'VEC_SCALE' and len(args) >= 3:
                # out = scale * v  elementwise
                v_id   = int(data[args[0]]); out_id = int(data[args[1]])
                scale  = float(data[args[2]]); n = int(data[args[3]]) if len(args)>3 else 999
                v   = farrays[v_id]   if v_id  < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(v), len(out))):
                    out[i] = scale * v[i]

            elif name == 'VEC_MUL' and len(args) >= 4:
                # out = a * b  elementwise
                a_id = int(data[args[0]]); b_id = int(data[args[1]])
                out_id = int(data[args[2]]); n = int(data[args[3]])
                a = farrays[a_id] if a_id < len(farrays) else []
                b = farrays[b_id] if b_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(a), len(b), len(out))):
                    out[i] = a[i] * b[i]

            elif name == 'VEC_SUB' and len(args) >= 4:
                # out = a - b  elementwise
                a_id = int(data[args[0]]); b_id = int(data[args[1]])
                out_id = int(data[args[2]]); n = int(data[args[3]])
                a = farrays[a_id] if a_id < len(farrays) else []
                b = farrays[b_id] if b_id < len(farrays) else []
                out = farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(a), len(b), len(out))):
                    out[i] = a[i] - b[i]

            elif name == 'VEC_SAXPY' and len(args) >= 5:
                # W -= lr * grad  (in-place weight update)
                # args: W_id, grad_id, n, lr_slot
                W_id   = int(data[args[0]]); g_id = int(data[args[1]])
                n      = int(data[args[2]]); lr   = float(data[args[3]])
                W = farrays[W_id] if W_id < len(farrays) else []
                g = farrays[g_id] if g_id < len(farrays) else []
                for i in range(min(n, len(W), len(g))):
                    W[i] -= lr * g[i]

            elif name == 'LEAKY_GRAD' and len(args) >= 3:
                # Derivative of leaky_relu(x): 1 if x>0 else 0.01
                # Apply elementwise: out[i] = dL[i] * leaky_grad(z[i])
                dL_id = int(data[args[0]]); z_id = int(data[args[1]])
                out_id= int(data[args[2]]); n    = int(data[args[3]]) if len(args)>3 else 999
                dL = farrays[dL_id] if dL_id < len(farrays) else []
                z  = farrays[z_id]  if z_id  < len(farrays) else []
                out= farrays[out_id] if out_id < len(farrays) else []
                for i in range(min(n, len(dL), len(z), len(out))):
                    grad = 1.0 if z[i] > 0 else 0.01
                    out[i] = dL[i] * grad

            elif name == 'SOFTMAX_CROSS_GRAD' and len(args) >= 4:
                # Combined softmax + cross-entropy gradient
                # prob[i] - onehot[true_class]  (already computed softmax)
                # args: prob_id, true_label_slot, out_id, n_classes
                prob_id    = int(data[args[0]])
                true_label = int(data[args[1]])
                out_id     = int(data[args[2]])
                n_classes  = int(data[args[3]])
                prob = farrays[prob_id] if prob_id < len(farrays) else []
                out  = farrays[out_id]  if out_id  < len(farrays) else []
                for i in range(min(n_classes, len(prob), len(out))):
                    out[i] = prob[i] - (1.0 if i == true_label else 0.0)

            elif name == 'CROSS_ENTROPY_LOSS' and len(args) >= 3:
                # loss = -log(prob[true_class])
                prob_id    = int(data[args[0]])
                true_label = int(data[args[1]])
                out_slot   = args[2]; ext(out_slot)
                prob = farrays[prob_id] if prob_id < len(farrays) else []
                if true_label < len(prob):
                    p = max(prob[true_label], 1e-10)
                    data[out_slot] = -math.log(p)
                else:
                    data[out_slot] = 10.0

            elif name == 'ZERO_ARR' and len(args) >= 2:
                # Zero out a float array
                arr_id = int(data[args[0]]); n = int(data[args[1]])
                arr = farrays[arr_id] if arr_id < len(farrays) else []
                for i in range(min(n, len(arr))): arr[i] = 0.0

            elif name == 'COPY_ARR' and len(args) >= 3:
                # Copy src array to dst
                src_id = int(data[args[0]]); dst_id = int(data[args[1]])
                n = int(data[args[2]])
                src = farrays[src_id] if src_id < len(farrays) else []
                dst = farrays[dst_id] if dst_id < len(farrays) else []
                for i in range(min(n, len(src), len(dst))): dst[i] = src[i]

            elif name == 'PRINT' and len(args) >= 1:
                v = data[args[0]]; self.output.append(v)

            elif name == 'FPRINT_S' and len(args) >= 1:
                v = data[args[0]]; self.output.append(v)

            elif name == 'ADD' and len(args) >= 3:
                ext(args[2]); data[args[2]] = (data[args[0]]+data[args[1]])&0xFFFF
            elif name == 'LOAD' and len(args) >= 2:
                ext(args[1]); data[args[1]] = data[args[0]]
            elif name == 'FADD_S' and len(args) >= 3:
                ext(args[2]); data[args[2]] = data[args[0]] + data[args[1]]
            elif name == 'FSUB_S' and len(args) >= 3:
                ext(args[2]); data[args[2]] = data[args[0]] - data[args[1]]
            elif name == 'FMUL_S' and len(args) >= 3:
                ext(args[2]); data[args[2]] = data[args[0]] * data[args[1]]
            elif name == 'FDIV_S' and len(args) >= 3:
                ext(args[2])
                data[args[2]] = data[args[0]]/data[args[1]] if data[args[1]] else 0.0
            elif name == 'INT_TO_FLOAT' and len(args) >= 2:
                ext(args[1]); data[args[1]] = float(data[args[0]])
            elif name == 'FLOAT_TO_INT' and len(args) >= 2:
                ext(args[1]); data[args[1]] = int(data[args[0]])

            pc += 1

        return data, farrays


# ══════════════════════════════════════════════════════════════
# ON-DEVICE LEARNING STREAM BUILDER
# Builds a ZCE bitstream that does a full forward+backward+update
# ══════════════════════════════════════════════════════════════

def build_learning_stream(weights, op_def, X_train, y_train,
                          X_eval, y_eval, lr=0.05, epochs=1):
    """
    Build a ZCE bitstream that:
    1. Loads weights into VM float arrays
    2. For each training sample:
       a. Forward pass
       b. Compute loss
       c. Backward pass (compute gradients)
       d. Update weights in-place
    3. Runs evaluation on eval set
    4. Prints predictions

    This is a complete learning loop inside a single ZCE bitstream.
    The VM does ALL the computation — no numpy involved in learning.
    """
    W1=weights['W1']; b1=weights['b1']
    W2=weights['W2']; b2=weights['b2']
    rows1,cols1=W1.shape; rows2,cols2=W2.shape

    data_values=[]; float_slots=set()
    def af(f):
        i=len(data_values); data_values.append(float(f)); float_slots.add(i); return i
    def ai(v):
        i=len(data_values); data_values.append(int(v)&0xFFFF); return i

    # Load weights
    W1_start=len(data_values)
    for v in W1.flatten(): af(v)
    b1_start=len(data_values)
    for v in b1: af(v)
    W2_start=len(data_values)
    for v in W2.flatten(): af(v)
    b2_start=len(data_values)
    for v in b2: af(v)

    # Scalar constants
    rows1_s=ai(rows1); cols1_s=ai(cols1)
    rows2_s=ai(rows2); cols2_s=ai(cols2)
    n1_s=ai(rows1); n2_s=ai(rows2); n_in_s=ai(cols1)
    W1_size_s=ai(rows1*cols1); b1_size_s=ai(rows1)
    W2_size_s=ai(rows2*cols2); b2_size_s=ai(rows2)

    # Learning rate
    lr_slot=af(lr)
    neg_lr_slot=af(-lr)

    # Array ID slots
    W1a=ai(0); b1a=ai(0); W2a=ai(0); b2a=ai(0)
    xa=ai(0); ha=ai(0); z1a=ai(0); oa=ai(0); proba=ai(0)
    # Gradient arrays
    dL2a=ai(0)   # gradient at output layer
    dha=ai(0)    # gradient at hidden layer (before activation)
    dz1a=ai(0)   # gradient through activation
    # Scratch
    tmp1a=ai(0); tmp2a=ai(0)
    # Output
    pred_s=ai(0); loss_s=af(0.0)
    op_id_s=ai(op_def['op_id'])
    true_label_s=ai(0)

    instrs=[]; D=D_TOP
    def I(op,args=None,**kw):
        instrs.append({'op':op,'args':args or [],'depth':D,**kw})

    # Define activation op
    I('DEFINE_OP',op_id=op_def['op_id'],n_inputs=op_def['n_inputs'],
      n_outputs=op_def['n_outputs'],steps=op_def['steps'])

    # Allocate arrays
    I('FARR_NEW',[W1_size_s,W1a]); I('FARR_NEW',[b1_size_s,b1a])
    I('FARR_NEW',[W2_size_s,W2a]); I('FARR_NEW',[b2_size_s,b2a])
    I('FARR_NEW',[n_in_s,xa])
    I('FARR_NEW',[n1_s,ha]); I('FARR_NEW',[n1_s,z1a])
    I('FARR_NEW',[n2_s,oa]); I('FARR_NEW',[n2_s,proba])
    I('FARR_NEW',[n2_s,dL2a]); I('FARR_NEW',[n1_s,dha])
    I('FARR_NEW',[n1_s,dz1a])
    I('FARR_NEW',[n1_s,tmp1a]); I('FARR_NEW',[n2_s,tmp2a])

    # Load weights into arrays
    for i,slot in enumerate(range(W1_start,W1_start+rows1*cols1)):
        I('FSET',[W1a,ai(i),slot])
    for i,slot in enumerate(range(b1_start,b1_start+rows1)):
        I('FSET',[b1a,ai(i),slot])
    for i,slot in enumerate(range(W2_start,W2_start+rows2*cols2)):
        I('FSET',[W2a,ai(i),slot])
    for i,slot in enumerate(range(b2_start,b2_start+rows2)):
        I('FSET',[b2a,ai(i),slot])

    # ── TRAINING LOOP ─────────────────────────────────────
    for epoch in range(epochs):
        for s_idx in range(len(X_train)):
            true_label = int(y_train[s_idx])

            # Load input
            for fi in range(X_train.shape[1]):
                fs=af(float(X_train[s_idx,fi])); I('FSET',[xa,ai(fi),fs])

            # Set true label
            tl_s=ai(true_label); I('LOAD',[tl_s,true_label_s])

            # ── FORWARD PASS ──
            # z1 = W1 @ x + b1
            I('MAT_VEC',[W1a,xa,z1a,rows1_s,cols1_s])
            I('VEC_ADD',[z1a,b1a,z1a,n1_s])
            # h = activation(z1)  — save z1 for backward
            I('COPY_ARR',[z1a,ha,n1_s])
            I('CALL_OP',[op_id_s,ha,ha,n1_s])
            # o = W2 @ h + b2
            I('MAT_VEC',[W2a,ha,oa,rows2_s,cols2_s])
            I('VEC_ADD',[oa,b2a,oa,n2_s])
            # prob = softmax(o)
            I('COPY_ARR',[oa,proba,n2_s])
            I('SOFTMAX_VEC',[proba,proba,n2_s])
            # loss = cross_entropy(prob, true_label)
            I('CROSS_ENTROPY_LOSS',[proba,true_label_s,loss_s])

            # ── BACKWARD PASS ──
            # dL2 = prob - onehot(true_label)  [softmax+CE combined gradient]
            I('SOFTMAX_CROSS_GRAD',[proba,true_label_s,dL2a,n2_s])

            # Update W2: W2 -= lr * outer(dL2, h)
            I('OUTER_ADD',[W2a,dL2a,ha,rows2_s,cols2_s,neg_lr_slot])

            # Update b2: b2 -= lr * dL2
            I('VEC_SAXPY',[b2a,dL2a,n2_s,neg_lr_slot])

            # dh = W2^T @ dL2
            I('MAT_VEC_T',[W2a,dL2a,dha,rows2_s,cols2_s])

            # dz1 = dh * activation_grad(z1)
            I('LEAKY_GRAD',[dha,z1a,dz1a,n1_s])

            # Update W1: W1 -= lr * outer(dz1, x)
            I('OUTER_ADD',[W1a,dz1a,xa,rows1_s,cols1_s,neg_lr_slot])

            # Update b1: b1 -= lr * dz1
            I('VEC_SAXPY',[b1a,dz1a,n1_s,neg_lr_slot])

    # ── EVALUATION ────────────────────────────────────────
    for s_idx in range(len(X_eval)):
        for fi in range(X_eval.shape[1]):
            fs=af(float(X_eval[s_idx,fi])); I('FSET',[xa,ai(fi),fs])
        I('MAT_VEC',[W1a,xa,ha,rows1_s,cols1_s])
        I('VEC_ADD',[ha,b1a,ha,n1_s])
        I('CALL_OP',[op_id_s,ha,ha,n1_s])
        I('MAT_VEC',[W2a,ha,oa,rows2_s,cols2_s])
        I('VEC_ADD',[oa,b2a,oa,n2_s])
        I('SOFTMAX_VEC',[oa,oa,n2_s])
        I('ARGMAX',[oa,n2_s,pred_s])
        I('PRINT',[pred_s])

    # Also need COPY_ARR, ZERO_ARR, OUTER_ADD, MAT_VEC_T,
    # VEC_SAXPY, LEAKY_GRAD, SOFTMAX_CROSS_GRAD, CROSS_ENTROPY_LOSS
    # registered as valid op names in the encoder
    # We use a trick: emit them as raw FLOAT_INSTR with custom codes
    # Actually — encode them as named ops the LearningVM handles directly
    return encode_learning(instrs, data_values, float_slots)


def encode_learning(instructions, data_values, float_slots=None):
    """
    Extended encoder that handles learning ops as named instructions.
    Maps new op names to tok(17,...) + elias(subcode).
    """
    if float_slots is None: float_slots = set()

    LEARNING_OPS = {
        'MAT_VEC_T':           1,
        'OUTER_ADD':           2,
        'VEC_SCALE':           3,
        'VEC_MUL':             4,
        'VEC_SUB':             5,
        'VEC_SAXPY':           6,
        'LEAKY_GRAD':          7,
        'SOFTMAX_CROSS_GRAD':  8,
        'CROSS_ENTROPY_LOSS':  9,
        'ZERO_ARR':           10,
        'COPY_ARR':           11,
    }
    LEARNING_ARITY = {
        'MAT_VEC_T':5, 'OUTER_ADD':6, 'VEC_SCALE':4, 'VEC_MUL':4,
        'VEC_SUB':4, 'VEC_SAXPY':4, 'LEAKY_GRAD':4,
        'SOFTMAX_CROSS_GRAD':4, 'CROSS_ENTROPY_LOSS':3,
        'ZERO_ARR':2, 'COPY_ARR':3,
    }

    from zce_arch_test import FLOAT_INSTR_R, INSTR_R, tok, ptr, eg_enc, raw16, f32_enc

    g = [tok(7,1), tok(5,1)]

    for instr in instructions:
        op   = instr['op']
        args = instr.get('args', [])
        d    = instr.get('depth', D_TOP)

        if op in LEARNING_OPS:
            # Encode as tok(17, depth) + elias(subcode) + args
            g.append(tok(17, d))
            g.append(ptr(LEARNING_OPS[op]))
            for a in args: g.append(ptr(a))

        elif op == 'DEFINE_OP':
            g.append(tok(15, d))
            g.append(ptr(instr['op_id']))
            g.append(ptr(instr['n_inputs']))
            g.append(ptr(instr['n_outputs']))
            g.append(ptr(len(instr['steps'])))
            for (pcode,a,b,c) in instr['steps']:
                g.append(ptr(pcode)); g.append(ptr(a))
                g.append(ptr(b));     g.append(ptr(c))

        elif op == 'CALL_OP':
            g.append(tok(16, d))
            for a in args: g.append(ptr(a))

        elif op in FLOAT_INSTR_R:
            g.append(tok(14,d)); g.append(tok(FLOAT_INSTR_R[op],d))
            for a in args: g.append(ptr(a))

        elif op in INSTR_R:
            g.append(tok(2,d)); g.append(tok(INSTR_R[op],d))
            for a in args: g.append(ptr(a))

        # Unknown ops silently skipped

    g += [tok(5,1), tok(7,1)]
    grammar = ''.join(g)

    data_parts = []
    for i,v in enumerate(data_values):
        if i in float_slots: data_parts.append(f32_enc(v))
        else: data_parts.append(eg_enc(int(v) if not isinstance(v,float) else 0))
    data_enc = ''.join(data_parts)
    header = raw16(len(grammar)) + raw16(len(data_values))
    return header + grammar + data_enc, float_slots


def decode_learning(bs, float_slots=None):
    """Extended decoder that handles tok(17,...) learning ops."""
    from zce_arch_test import (r16, eg_dec, f32_dec, FLOAT_INSTR, FLOAT_INSTR_ARITY,
                                INSTR, INSTR_ARITY)

    LEARNING_OPS = {
        1:'MAT_VEC_T', 2:'OUTER_ADD', 3:'VEC_SCALE', 4:'VEC_MUL',
        5:'VEC_SUB', 6:'VEC_SAXPY', 7:'LEAKY_GRAD',
        8:'SOFTMAX_CROSS_GRAD', 9:'CROSS_ENTROPY_LOSS',
        10:'ZERO_ARR', 11:'COPY_ARR',
    }
    LEARNING_ARITY = {
        'MAT_VEC_T':5, 'OUTER_ADD':6, 'VEC_SCALE':4, 'VEC_MUL':4,
        'VEC_SUB':4, 'VEC_SAXPY':4, 'LEAKY_GRAD':4,
        'SOFTMAX_CROSS_GRAD':4, 'CROSS_ENTROPY_LOSS':3,
        'ZERO_ARR':2, 'COPY_ARR':3,
    }

    if float_slots is None: float_slots = set()
    gl=r16(bs[:16]); dc=r16(bs[16:32])
    gram=bs[32:32+gl]; draw=bs[32+gl:]
    pos2,data=0,[]
    for i in range(dc):
        if i in float_slots: data.append(f32_dec(draw[pos2:pos2+32])); pos2+=32
        else: v,pos2=eg_dec(draw,pos2); data.append(v)

    user_ops={}; ops=[]; pos=0

    def rp():
        nonlocal pos; v,pos=eg_dec(gram,pos); return v
    def rt():
        nonlocal pos
        n=0
        while pos<len(gram) and gram[pos]=='0': n+=1; pos+=1
        m=0
        while pos<len(gram) and gram[pos]=='1': m+=1; pos+=1
        if pos<len(gram) and gram[pos]=='0': pos+=1
        return n,m

    while pos<len(gram):
        n,depth=rt()
        if n==0: continue
        if n in (7,5): continue
        if n==15:
            op_id=rp(); n_in=rp(); n_out=rp(); n_steps=rp()
            steps=[]
            for _ in range(n_steps):
                pcode=rp(); a=rp(); b=rp(); c=rp(); steps.append((pcode,a,b,c))
            user_ops[op_id]={'n_inputs':n_in,'n_outputs':n_out,'steps':steps}
            ops.append({'op':'DEFINE_OP','op_id':op_id,'user_ops':user_ops,'depth':depth})
        elif n==16:
            op_id=rp(); x_s=rp(); out_s=rp(); n_s=rp()
            ops.append({'op':'CALL_OP','args':[op_id,x_s,out_s,n_s],
                        'user_ops':user_ops,'depth':depth})
        elif n==17:
            subcode=rp(); lop=LEARNING_OPS.get(subcode,f'UNK_L{subcode}')
            arity=LEARNING_ARITY.get(lop,0)
            largs=[rp() for _ in range(arity)]
            ops.append({'op':lop,'args':largs,'depth':depth})
        elif n==14:
            ic,_=rt(); iop=FLOAT_INSTR.get(ic,f'UNK_F{ic}')
            arity=FLOAT_INSTR_ARITY.get(iop,0); iargs=[rp() for _ in range(arity)]
            ops.append({'op':iop,'args':iargs,'depth':depth})
        elif n==2:
            ic,_=rt(); iop=INSTR.get(ic,f'UNK{ic}')
            arity=INSTR_ARITY.get(iop,0); iargs=[rp() for _ in range(arity)]
            ops.append({'op':iop,'args':iargs,'depth':depth})

    return ops,data


# Patch LearningVM to use extended decoder
_orig_run = LearningVM.run
def _patched_run(self, bitstream, float_slots=None):
    # Temporarily swap decode
    import zce_arch_test as _zce
    _orig_decode = _zce.decode
    _zce.decode = decode_learning
    result = _orig_run(self, bitstream, float_slots)
    _zce.decode = _orig_decode
    return result
LearningVM.run = _patched_run


# ══════════════════════════════════════════════════════════════
# DATASET
# ══════════════════════════════════════════════════════════════

def make_moons(n=300, noise=0.2, seed=42):
    rng=np.random.RandomState(seed); n2=n//2
    t=np.linspace(0,np.pi,n2)
    X0=np.c_[np.cos(t),np.sin(t)]
    X1=np.c_[1-np.cos(t),1-np.sin(t)-0.5]
    X=np.vstack([X0,X1]).astype(np.float32)
    X+=rng.randn(*X.shape).astype(np.float32)*noise
    X=(X-X.mean(0))/(X.std(0)+1e-8)
    y=np.array([0]*n2+[1]*n2)
    return X.astype(np.float32),y

def np_acc(W1,b1,W2,b2,act_fn,X,y):
    z1=X@W1.T+b1; h=np.vectorize(act_fn)(z1)
    z2=h@W2.T+b2; z2-=z2.max(1,keepdims=True)
    e=np.exp(z2)
    return float(np.mean(np.argmax(e/e.sum(1,keepdims=True),1)==y))


# ══════════════════════════════════════════════════════════════
# TEST 1: ON-DEVICE LEARNING FROM SCRATCH
# ══════════════════════════════════════════════════════════════

section("TEST 1: ON-DEVICE LEARNING FROM SCRATCH")
print("  Random weights → learn inside the VM → measure accuracy.")
print("  No numpy in the learning loop. VM does all the math.\n")

X,y = make_moons(n=200, noise=0.2)
X_eval,y_eval = make_moons(n=100, noise=0.2, seed=99)

leaky_fn = lambda x: max(0.0,x)+0.01*min(0.0,x)
op_def = make_leaky_relu_1input(0.01)

# Start with random weights
np.random.seed(42)
w_random = {
    'W1': (np.random.randn(8,2)*0.5).astype(np.float32),
    'b1': np.zeros(8, dtype=np.float32),
    'W2': (np.random.randn(2,8)*0.5).astype(np.float32),
    'b2': np.zeros(2, dtype=np.float32),
    'activation': 'leaky_relu', 'alpha': 0.01,
    'X_sample': X[:5], 'y_sample': y[:5],
}

acc_before = np_acc(w_random['W1'],w_random['b1'],
                    w_random['W2'],w_random['b2'],leaky_fn,X_eval,y_eval)
print(f"  Accuracy with random weights: {acc_before:.3f}")

# Build learning stream — 3 epochs of on-device training
print(f"  Building ZCE learning stream (3 epochs, {len(X)} samples)...")
t0=time.time()
bc_learn, fs_learn = build_learning_stream(
    w_random, op_def,
    X_train=X, y_train=y,
    X_eval=X_eval[:20], y_eval=y_eval[:20],
    lr=0.05, epochs=3
)
t_build = time.time()-t0
print(f"  Stream size: {len(bc_learn)//8:,} bytes")
print(f"  Build time: {t_build:.1f}s")

print(f"  Running learning stream in VM...")
t0=time.time()
vm=LearningVM()
vm.run(bc_learn, fs_learn)
t_run=time.time()-t0

preds=[int(v) for v in vm.output]
true=list(y_eval[:20])
acc_after_zce=sum(p==t for p,t in zip(preds,true))/len(true)

print(f"  VM run time: {t_run:.1f}s")
print(f"  Predictions: {preds}")
print(f"  True labels: {true}")
print(f"  Accuracy after on-device learning: {acc_after_zce:.3f}")
print(f"  Improvement: {acc_after_zce-acc_before:+.3f}")
t1_pass = acc_after_zce > acc_before + 0.05
print(f"  {PASS if t1_pass else FAIL}")


# ══════════════════════════════════════════════════════════════
# TEST 2: ON-DEVICE ADAPTATION TO NEW DATA
# ══════════════════════════════════════════════════════════════

section("TEST 2: ON-DEVICE ADAPTATION TO DISTRIBUTION SHIFT")
print("  Pre-train model on distribution A (numpy, fast).")
print("  Expose to distribution B — accuracy drops.")
print("  Run on-device learning stream on B data.")
print("  Measure recovery — all inside the VM.\n")

# Distribution A
Xa,ya = make_moons(n=300, noise=0.15, seed=1)
# Distribution B — shifted
rng=np.random.RandomState(7); n2=100
t=np.linspace(0,np.pi,n2)
Xb0=np.c_[np.cos(t)+1.5, np.sin(t)*0.7]
Xb1=np.c_[1.5-np.cos(t), 0.7-np.sin(t)-0.3]
Xb=np.vstack([Xb0,Xb1]).astype(np.float32)
Xb+=rng.randn(*Xb.shape).astype(np.float32)*0.15
Xb=(Xb-Xb.mean(0))/(Xb.std(0)+1e-8); yb=np.array([0]*n2+[1]*n2)
Xb_eval,yb_eval=make_moons(n=100,noise=0.15,seed=55)
# Normalize eval with B stats
Xb_eval=(Xb_eval-Xb.mean(0))/(Xb.std(0)+1e-8)

print("  Pre-training on distribution A...")
wA=train_model('leaky_relu',leaky_fn,hidden_size=8,
               X=Xa,y=ya,epochs=1500,lr=0.1)

acc_A = np_acc(wA['W1'],wA['b1'],wA['W2'],wA['b2'],leaky_fn,Xa,ya)
acc_B_before = np_acc(wA['W1'],wA['b1'],wA['W2'],wA['b2'],leaky_fn,Xb,yb)
print(f"  Accuracy on A: {acc_A:.3f}")
print(f"  Accuracy on B (before adaptation): {acc_B_before:.3f}")

# On-device adaptation to B
print(f"  Running on-device adaptation (2 epochs on B data)...")
t0=time.time()
bc_adapt,fs_adapt=build_learning_stream(
    wA, op_def,
    X_train=Xb[:80], y_train=yb[:80],
    X_eval=Xb[80:], y_eval=yb[80:],
    lr=0.03, epochs=2
)
vm2=LearningVM(); vm2.run(bc_adapt,fs_adapt)
t_adapt=time.time()-t0

preds_B=[int(v) for v in vm2.output]
true_B=list(yb[80:])
acc_B_after=sum(p==t for p,t in zip(preds_B,true_B))/len(true_B)

print(f"  Adaptation time: {t_adapt:.1f}s")
print(f"  Accuracy on B after adaptation: {acc_B_after:.3f}")
print(f"  Recovery: {acc_B_after-acc_B_before:+.3f}")
t2_pass = acc_B_after >= acc_B_before
print(f"  {PASS if t2_pass else FAIL}")


# ══════════════════════════════════════════════════════════════
# TEST 3: COMPARE VM LEARNING vs NUMPY LEARNING
# ══════════════════════════════════════════════════════════════

section("TEST 3: VM LEARNING vs NUMPY LEARNING — SAME DATA")
print("  Run exact same training on same data.")
print("  One in numpy. One in ZCE VM.")
print("  Compare final accuracy — should be close.\n")

X_t,y_t = make_moons(n=150, noise=0.2, seed=42)
X_v,y_v = make_moons(n=50,  noise=0.2, seed=77)

np.random.seed(0)
W1_init=(np.random.randn(8,2)*0.3).astype(np.float32)
b1_init=np.zeros(8,dtype=np.float32)
W2_init=(np.random.randn(2,8)*0.3).astype(np.float32)
b2_init=np.zeros(2,dtype=np.float32)

# NumPy training
W1=W1_init.copy(); b1=b1_init.copy()
W2=W2_init.copy(); b2=b2_init.copy()
act_v=np.vectorize(leaky_fn)
eps=1e-5; dact_v=np.vectorize(lambda x:(leaky_fn(x+eps)-leaky_fn(x-eps))/(2*eps))
def softmax(z):
    z=z-z.max(axis=1,keepdims=True); e=np.exp(z); return e/e.sum(axis=1,keepdims=True)

lr=0.05
for epoch in range(3):
    for i in range(len(X_t)):
        x=X_t[i:i+1]; yi=int(y_t[i])
        z1=x@W1.T+b1; h=act_v(z1)
        o=h@W2.T+b2; prob=softmax(o)
        Y=np.zeros((1,2)); Y[0,yi]=1.0
        dL=(prob-Y)
        dW2=dL.T@h; db2=dL.sum(0)
        dh=dL@W2; dz1=dh*dact_v(z1)
        dW1=dz1.T@x; db1=dz1.sum(0)
        W1-=lr*dW1; b1-=lr*db1; W2-=lr*dW2; b2-=lr*db2

np_final_acc = np_acc(W1,b1,W2,b2,leaky_fn,X_v,y_v)

# ZCE VM training — same init weights, same lr, same epochs
w_init={
    'W1':W1_init.copy(),'b1':b1_init.copy(),
    'W2':W2_init.copy(),'b2':b2_init.copy(),
    'activation':'leaky_relu','alpha':0.01,
    'X_sample':X_t[:5],'y_sample':y_t[:5],
}
bc_cmp,fs_cmp=build_learning_stream(
    w_init, op_def,
    X_train=X_t, y_train=y_t,
    X_eval=X_v[:20], y_eval=y_v[:20],
    lr=lr, epochs=3
)
vm3=LearningVM(); vm3.run(bc_cmp,fs_cmp)
preds_vm=[int(v) for v in vm3.output]
true_vm=list(y_v[:20])
vm_final_acc=sum(p==t for p,t in zip(preds_vm,true_vm))/len(true_vm)

print(f"  NumPy training accuracy:  {np_final_acc:.3f}")
print(f"  ZCE VM training accuracy: {vm_final_acc:.3f}")
print(f"  Difference: {abs(np_final_acc-vm_final_acc):.3f}")
t3_pass = abs(np_final_acc - vm_final_acc) < 0.15
print(f"  {PASS if t3_pass else FAIL} — VM and NumPy learning converge similarly")


# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════

section("SUMMARY — ON-DEVICE LEARNING")

print(f"  {'Test':<45} {'Result'}")
print(f"  {'-'*45} {'-'*15}")
print(f"  {'1. Learn from scratch in VM':<45} {PASS if t1_pass else FAIL}")
print(f"     random→learned: {acc_before:.3f} → {acc_after_zce:.3f}")
print(f"  {'2. Adapt to distribution shift in VM':<45} {PASS if t2_pass else FAIL}")
print(f"     B accuracy: {acc_B_before:.3f} → {acc_B_after:.3f}")
print(f"  {'3. VM learning matches NumPy':<45} {PASS if t3_pass else FAIL}")
print(f"     numpy={np_final_acc:.3f}  vm={vm_final_acc:.3f}")

print(f"""
  WHAT THIS MEANS:

  The ZCE VM now does the full learning loop:
    Forward pass → loss → backward pass → weight update

  This runs inside a single ZCE bitstream.
  No numpy. No external training pipeline.
  The model learns from data it receives, on the device.

  The VM extended cleanly:
    tok(17,...) = learning ops (MAT_VEC_T, OUTER_ADD, VEC_SAXPY, etc.)
    Backward pass expressed as VM instructions
    Weights updated in-place inside float arrays

  What this unlocks:
    A deployed model can receive raw data and improve itself.
    No server round-trip for learning.
    Architecture (grammar) + weights both live in the stream.
    Both can change. Both can improve. Continuously.

  Remaining honest gaps:
    • Learning rate scheduling not implemented
    • Batch gradient averaging not implemented  
    • This is SGD — more sophisticated optimizers need more ops
    • Speed: Python VM is slow — C runtime would fix this
""")
