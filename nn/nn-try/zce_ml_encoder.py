"""
zce_ml_encoder.py
=================
Encodes neural network forward passes as v2 ZCE bitstreams
for execution by zce_decoder_v2.h + zce_ml_exec.h

Op codes mirror zce_ml_exec.h exactly.
"""

import math
import struct
import numpy as np


# ── Elias gamma ──────────────────────────────────────────────

def elias(v):
    assert v >= 0, f"elias({v})"
    x = v + 1
    k = int(math.log2(x))
    return '0' * k + format(x, f'0{k+1}b')

def token(n, depth=1):
    return '0' * n + '1' * depth + '0'


# ── Arg types & actions ──────────────────────────────────────

ARG_PTR   = 0
ARG_VAL   = 1
ARG_RAW32 = 2

ACT_EXEC = 0
ACT_JIF  = 1
ACT_JMP  = 2
ACT_NOP  = 3

# Extended op codes
OP_SUB        = 3
OP_MUL        = 4
OP_DIV        = 5
OP_FSET       = 10
OP_FADD       = 11
OP_FSUB       = 12
OP_FMUL       = 13
OP_FDIV       = 14
OP_FEXP       = 15
OP_FTANH      = 16
OP_FMAX       = 17
OP_FMIN       = 18
OP_FNEG       = 19
OP_FABS       = 20
OP_FCMP_GT    = 21
OP_FPRINT     = 22
OP_FARR_NEW   = 30
OP_FARR_SET   = 31
OP_FARR_GET   = 32
OP_MAT_VEC    = 40
OP_VEC_ADD    = 41
OP_SOFTMAX    = 42
OP_ARGMAX     = 43
OP_LEAKY_RELU = 44
OP_VEC_COPY   = 45


# ── Two-pass encoder ─────────────────────────────────────────

class MLEncoder:
    """
    Two-pass encoder. Records instructions symbolically,
    then emits bits with correct label targets.
    """

    def __init__(self):
        self._instrs = []
        self._tok_defined = set()  # which token slots have been DEFINE_OP'd

    # ── Token definitions ─────────────────────────────────────

    def _ensure_defined(self, tok_n, arg_types, action, action_param=0):
        if tok_n not in self._tok_defined:
            self._instrs.append(('DEFINE_OP', tok_n, arg_types, action, action_param))
            self._tok_defined.add(tok_n)

    # ── Token slot assignments ────────────────────────────────
    # Base: 1=SET, 2=ADD, 3=JIF, 4=JMP, 5=DEFINE_OP
    # ML tokens start at 6

    TOK_SUB        = 6
    TOK_MUL        = 7
    TOK_DIV        = 8
    TOK_FSET       = 9   # FSET: dst PTR, raw32 value
    TOK_FADD       = 10
    TOK_FSUB       = 11
    TOK_FMUL       = 12
    TOK_FDIV       = 13
    TOK_FEXP       = 14
    TOK_FTANH      = 15
    TOK_FMAX       = 16
    TOK_FMIN       = 17
    TOK_FNEG       = 18
    TOK_FABS       = 19
    TOK_FCMP_GT    = 20
    TOK_FARR_NEW   = 21
    TOK_FARR_SET   = 22
    TOK_FARR_GET   = 23
    TOK_MAT_VEC    = 24
    TOK_VEC_ADD    = 25
    TOK_SOFTMAX    = 26
    TOK_ARGMAX     = 27
    TOK_LEAKY_RELU = 28
    TOK_VEC_COPY   = 29

    def _def_all(self):
        """Emit DEFINE_OP for all ML ops we'll use."""
        defs = [
            (self.TOK_SUB,        [ARG_PTR]*3,                   ACT_EXEC, OP_SUB),
            (self.TOK_MUL,        [ARG_PTR]*3,                   ACT_EXEC, OP_MUL),
            (self.TOK_DIV,        [ARG_PTR]*3,                   ACT_EXEC, OP_DIV),
            (self.TOK_FSET,       [ARG_PTR, ARG_RAW32],          ACT_EXEC, OP_FSET),
            (self.TOK_FADD,       [ARG_PTR]*3,                   ACT_EXEC, OP_FADD),
            (self.TOK_FSUB,       [ARG_PTR]*3,                   ACT_EXEC, OP_FSUB),
            (self.TOK_FMUL,       [ARG_PTR]*3,                   ACT_EXEC, OP_FMUL),
            (self.TOK_FDIV,       [ARG_PTR]*3,                   ACT_EXEC, OP_FDIV),
            (self.TOK_FEXP,       [ARG_PTR]*2,                   ACT_EXEC, OP_FEXP),
            (self.TOK_FTANH,      [ARG_PTR]*2,                   ACT_EXEC, OP_FTANH),
            (self.TOK_FMAX,       [ARG_PTR]*3,                   ACT_EXEC, OP_FMAX),
            (self.TOK_FMIN,       [ARG_PTR]*3,                   ACT_EXEC, OP_FMIN),
            (self.TOK_FNEG,       [ARG_PTR]*2,                   ACT_EXEC, OP_FNEG),
            (self.TOK_FABS,       [ARG_PTR]*2,                   ACT_EXEC, OP_FABS),
            (self.TOK_FCMP_GT,    [ARG_PTR]*3,                   ACT_EXEC, OP_FCMP_GT),
            (self.TOK_FARR_NEW,   [ARG_PTR]*2,                   ACT_EXEC, OP_FARR_NEW),
            (self.TOK_FARR_SET,   [ARG_PTR]*3,                   ACT_EXEC, OP_FARR_SET),
            (self.TOK_FARR_GET,   [ARG_PTR]*3,                   ACT_EXEC, OP_FARR_GET),
            (self.TOK_MAT_VEC,    [ARG_PTR]*5,                   ACT_EXEC, OP_MAT_VEC),
            (self.TOK_VEC_ADD,    [ARG_PTR]*4,                   ACT_EXEC, OP_VEC_ADD),
            (self.TOK_SOFTMAX,    [ARG_PTR]*2,                   ACT_EXEC, OP_SOFTMAX),
            (self.TOK_ARGMAX,     [ARG_PTR]*3,                   ACT_EXEC, OP_ARGMAX),
            (self.TOK_LEAKY_RELU, [ARG_PTR]*2,                   ACT_EXEC, OP_LEAKY_RELU),
            (self.TOK_VEC_COPY,   [ARG_PTR]*3,                   ACT_EXEC, OP_VEC_COPY),
        ]
        for (tok_n, arg_types, action, action_param) in defs:
            self._instrs.append(('DEFINE_OP', tok_n, arg_types, action, action_param))

    # ── Instruction emitters ──────────────────────────────────

    def label(self, name):
        self._instrs.append(('LABEL', name))

    def SET(self, dst, val):
        """Integer SET: slots[dst] = val"""
        self._instrs.append(('SET', dst, val))

    def ADD(self, dst, a, b):
        self._instrs.append(('ADD', dst, a, b))

    def JIF(self, cond, lbl):
        self._instrs.append(('JIF', cond, lbl))

    def JMP(self, lbl):
        self._instrs.append(('JMP', lbl))

    def SUB(self, dst, a, b):
        self._instrs.append(('CUSTOM', self.TOK_SUB, [dst, a, b]))

    def FSET(self, dst, f):
        """Float SET: fslots[dst] = f (float)"""
        bits = struct.unpack('I', struct.pack('f', float(f)))[0]
        self._instrs.append(('CUSTOM_RAW', self.TOK_FSET, [dst], bits))

    def FADD(self, dst, a, b):
        self._instrs.append(('CUSTOM', self.TOK_FADD, [dst, a, b]))

    def FMUL(self, dst, a, b):
        self._instrs.append(('CUSTOM', self.TOK_FMUL, [dst, a, b]))

    def FNEG(self, dst, a):
        self._instrs.append(('CUSTOM', self.TOK_FNEG, [dst, a]))

    def FEXP(self, dst, a):
        self._instrs.append(('CUSTOM', self.TOK_FEXP, [dst, a]))

    def FTANH(self, dst, a):
        self._instrs.append(('CUSTOM', self.TOK_FTANH, [dst, a]))

    def FARR_NEW(self, dst_slot, size_slot):
        self._instrs.append(('CUSTOM', self.TOK_FARR_NEW, [dst_slot, size_slot]))

    def FARR_SET(self, arr_slot, idx_slot, fval_slot):
        self._instrs.append(('CUSTOM', self.TOK_FARR_SET, [arr_slot, idx_slot, fval_slot]))

    def FARR_GET(self, dst_fslot, arr_slot, idx_slot):
        self._instrs.append(('CUSTOM', self.TOK_FARR_GET, [dst_fslot, arr_slot, idx_slot]))

    def MAT_VEC(self, out_slot, W_slot, x_slot, rows_slot, cols_slot):
        self._instrs.append(('CUSTOM', self.TOK_MAT_VEC,
                              [out_slot, W_slot, x_slot, rows_slot, cols_slot]))

    def VEC_ADD(self, out_slot, a_slot, b_slot, n_slot):
        self._instrs.append(('CUSTOM', self.TOK_VEC_ADD, [out_slot, a_slot, b_slot, n_slot]))

    def SOFTMAX(self, arr_slot, n_slot):
        self._instrs.append(('CUSTOM', self.TOK_SOFTMAX, [arr_slot, n_slot]))

    def ARGMAX(self, dst_slot, arr_slot, n_slot):
        self._instrs.append(('CUSTOM', self.TOK_ARGMAX, [dst_slot, arr_slot, n_slot]))

    def LEAKY_RELU(self, arr_slot, n_slot):
        self._instrs.append(('CUSTOM', self.TOK_LEAKY_RELU, [arr_slot, n_slot]))

    # ── Emit one instruction to bits ─────────────────────────

    def _emit(self, instr, labels):
        kind = instr[0]
        if kind == 'LABEL':
            return ''
        elif kind == 'DEFINE_OP':
            _, tok_n, arg_types, action, action_param = instr
            b = token(5)
            b += elias(tok_n)
            b += elias(len(arg_types) - 1)
            for at in arg_types: b += elias(at)
            b += elias(action)
            if action == ACT_EXEC: b += elias(action_param)
            return b
        elif kind == 'SET':
            _, dst, val = instr
            return token(1) + elias(dst) + elias(val)
        elif kind == 'ADD':
            _, dst, a, b = instr
            return token(2) + elias(dst) + elias(a) + elias(b)
        elif kind == 'JIF':
            _, cond, lbl = instr
            tgt = labels.get(lbl, 0)
            return token(3) + elias(cond) + elias(tgt)
        elif kind == 'JMP':
            _, lbl = instr
            tgt = labels.get(lbl, 0)
            return token(4) + elias(tgt)
        elif kind == 'CUSTOM':
            _, tok_n, args = instr
            b = token(tok_n)
            for a in args: b += elias(a)
            return b
        elif kind == 'CUSTOM_RAW':
            # CUSTOM_RAW: tok_n, [ptr_args], raw32_value
            _, tok_n, ptr_args, raw_val = instr
            b = token(tok_n)
            for a in ptr_args: b += elias(a)
            b += format(raw_val & 0xFFFFFFFF, '032b')
            return b
        return ''

    # ── Two-pass build ────────────────────────────────────────

    def build(self):
        labels = {}
        # Iterate to convergence (label positions affect elias lengths)
        for _ in range(20):
            pos = 0
            new_labels = {}
            for instr in self._instrs:
                if instr[0] == 'LABEL':
                    new_labels[instr[1]] = pos
                else:
                    pos += len(self._emit(instr, labels))
            if new_labels == labels:
                break
            labels = new_labels

        # Final pass
        grammar = ''
        for instr in self._instrs:
            grammar += self._emit(instr, labels)

        header = elias(len(grammar))
        full = header + grammar
        pad = (8 - len(full) % 8) % 8
        full += '0' * pad
        return bytes(int(full[i:i+8], 2) for i in range(0, len(full), 8))


# ── Slot allocator ────────────────────────────────────────────

class SlotAlloc:
    """Tracks slot assignments for int and float slots."""
    def __init__(self, start=0):
        self._next = start
    def alloc(self, n=1):
        s = self._next
        self._next += n
        return s
    def next(self):
        return self._next


# ── Network encoder ───────────────────────────────────────────

def encode_mlp_forward(W1, b1, W2, b2, X_samples, activation='leaky_relu'):
    """
    Encode a 2-layer MLP forward pass.
    W1: (hidden, input), b1: (hidden,)
    W2: (n_class, hidden), b2: (n_class,)
    X_samples: list/array of input vectors

    Slot layout (integer slots):
      0..3     : size constants (n_in, n_hidden, n_out, scratch)
      4..7     : array IDs (W1_arr, b1_arr, W2_arr, b2_arr)
      8..11    : array IDs (x_arr, h_arr, out_arr, scratch)
      12       : prediction output
      100..199 : float scalar temps
    """
    W1 = np.array(W1, dtype=np.float32)
    b1 = np.array(b1, dtype=np.float32)
    W2 = np.array(W2, dtype=np.float32)
    b2 = np.array(b2, dtype=np.float32)

    n_in     = W1.shape[1]
    n_hidden = W1.shape[0]
    n_out    = W2.shape[0]

    enc = MLEncoder()
    enc._def_all()   # emit all DEFINE_OPs upfront

    # ── Integer constant slots ────────────────────────────────
    S_N_IN     = 0
    S_N_HIDDEN = 1
    S_N_OUT    = 2
    S_W1_SIZE  = 3   # n_hidden * n_in
    S_W2_SIZE  = 4   # n_out * n_hidden

    # Array ID slots
    S_W1_ARR = 10
    S_B1_ARR = 11
    S_W2_ARR = 12
    S_B2_ARR = 13
    S_X_ARR  = 14
    S_H_ARR  = 15
    S_OUT_ARR= 16
    S_IDX    = 17   # scratch index
    S_PRED   = 18   # prediction result

    # Float scalar slots (for loading weights one at a time)
    S_FTMP   = 2000  # float temp — high slot, never collides with result slots (50+n)

    # ── Emit size constants ───────────────────────────────────
    enc.SET(S_N_IN,     n_in)
    enc.SET(S_N_HIDDEN, n_hidden)
    enc.SET(S_N_OUT,    n_out)
    enc.SET(S_W1_SIZE,  n_hidden * n_in)
    enc.SET(S_W2_SIZE,  n_out * n_hidden)

    # ── Allocate float arrays ─────────────────────────────────
    enc.FARR_NEW(S_W1_ARR, S_W1_SIZE)
    enc.FARR_NEW(S_B1_ARR, S_N_HIDDEN)
    enc.FARR_NEW(S_W2_ARR, S_W2_SIZE)
    enc.FARR_NEW(S_B2_ARR, S_N_OUT)
    enc.FARR_NEW(S_X_ARR,  S_N_IN)
    enc.FARR_NEW(S_H_ARR,  S_N_HIDDEN)
    enc.FARR_NEW(S_OUT_ARR, S_N_OUT)

    # ── Load W1 ───────────────────────────────────────────────
    for i, v in enumerate(W1.flatten()):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_W1_ARR, S_IDX, S_FTMP)

    # ── Load b1 ───────────────────────────────────────────────
    for i, v in enumerate(b1):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_B1_ARR, S_IDX, S_FTMP)

    # ── Load W2 ───────────────────────────────────────────────
    for i, v in enumerate(W2.flatten()):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_W2_ARR, S_IDX, S_FTMP)

    # ── Load b2 ───────────────────────────────────────────────
    for i, v in enumerate(b2):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_B2_ARR, S_IDX, S_FTMP)

    # ── Forward pass for each sample ─────────────────────────
    for s_idx, x in enumerate(X_samples):
        x = np.array(x, dtype=np.float32)

        # Load input
        for i, v in enumerate(x):
            enc.SET(S_IDX, i)
            enc.FSET(S_FTMP, float(v))
            enc.FARR_SET(S_X_ARR, S_IDX, S_FTMP)

        # Layer 1: h = W1 @ x + b1
        enc.MAT_VEC(S_H_ARR, S_W1_ARR, S_X_ARR, S_N_HIDDEN, S_N_IN)
        enc.VEC_ADD(S_H_ARR, S_H_ARR, S_B1_ARR, S_N_HIDDEN)

        # Activation
        if activation == 'leaky_relu':
            enc.LEAKY_RELU(S_H_ARR, S_N_HIDDEN)
        elif activation == 'tanh':
            # Apply tanh element-by-element using FARR_GET/FTANH/FARR_SET loop
            # For simplicity, inline it for each element
            for i in range(n_hidden):
                enc.SET(S_IDX, i)
                enc.FARR_GET(S_FTMP, S_H_ARR, S_IDX)
                enc.FTANH(S_FTMP, S_FTMP)
                enc.FARR_SET(S_H_ARR, S_IDX, S_FTMP)

        # Layer 2: out = W2 @ h + b2
        enc.MAT_VEC(S_OUT_ARR, S_W2_ARR, S_H_ARR, S_N_OUT, S_N_HIDDEN)
        enc.VEC_ADD(S_OUT_ARR, S_OUT_ARR, S_B2_ARR, S_N_OUT)

        # Softmax
        enc.SOFTMAX(S_OUT_ARR, S_N_OUT)

        # Argmax → prediction in S_PRED
        enc.ARGMAX(S_PRED, S_OUT_ARR, S_N_OUT)

        # Store prediction in slot (20 + s_idx) for retrieval
        enc.ADD(20 + s_idx, S_PRED, 0)   # copy via ADD with slot[0]=0 trick
        # Actually SET doesn't work for slot values, use SUB self trick:
        # Better: just read S_PRED after each sample from the decoder
        # Since we run sequentially, S_PRED will hold last prediction
        # For multi-sample, store in different slots via ADD
        # slot[0] is always 0 after SET(0,0)... not reliable
        # Cleanest: emit a "store prediction" as ADD(result_slot, S_PRED, zero_slot)
        # We'll use slot 50+s_idx as result, with a known-zero slot

    # Ensure slot 0 = 0 as a zero register (emit at very start)
    # Actually let's rebuild with zero slot

    return enc.build()


def encode_mlp_forward_v2(W1, b1, W2, b2, X_samples, activation='leaky_relu'):
    """
    Cleaner version: results stored in slots 50, 51, 52...
    Uses slot 49 as a zero register.
    """
    W1 = np.array(W1, dtype=np.float32)
    b1 = np.array(b1, dtype=np.float32)
    W2 = np.array(W2, dtype=np.float32)
    b2 = np.array(b2, dtype=np.float32)
    X_samples = [np.array(x, dtype=np.float32) for x in X_samples]

    n_in     = W1.shape[1]
    n_hidden = W1.shape[0]
    n_out    = W2.shape[0]

    enc = MLEncoder()
    enc._def_all()

    # Slot assignments
    S_ZERO     = 0
    S_N_IN     = 1
    S_N_HIDDEN = 2
    S_N_OUT    = 3
    S_W1_SIZE  = 4
    S_W2_SIZE  = 5
    S_W1_ARR   = 6
    S_B1_ARR   = 7
    S_W2_ARR   = 8
    S_B2_ARR   = 9
    S_X_ARR    = 10
    S_H_ARR    = 11
    S_OUT_ARR  = 12
    S_IDX      = 13
    S_PRED     = 14
    S_FTMP     = 2000  # float temp — must be > 50+max_samples

    # Zero register and sizes
    enc.SET(S_ZERO,     0)
    enc.SET(S_N_IN,     n_in)
    enc.SET(S_N_HIDDEN, n_hidden)
    enc.SET(S_N_OUT,    n_out)
    enc.SET(S_W1_SIZE,  n_hidden * n_in)
    enc.SET(S_W2_SIZE,  n_out * n_hidden)

    # Allocate arrays
    enc.FARR_NEW(S_W1_ARR, S_W1_SIZE)
    enc.FARR_NEW(S_B1_ARR, S_N_HIDDEN)
    enc.FARR_NEW(S_W2_ARR, S_W2_SIZE)
    enc.FARR_NEW(S_B2_ARR, S_N_OUT)
    enc.FARR_NEW(S_X_ARR,  S_N_IN)
    enc.FARR_NEW(S_H_ARR,  S_N_HIDDEN)
    enc.FARR_NEW(S_OUT_ARR, S_N_OUT)

    # Load W1
    for i, v in enumerate(W1.flatten()):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_W1_ARR, S_IDX, S_FTMP)

    # Load b1
    for i, v in enumerate(b1):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_B1_ARR, S_IDX, S_FTMP)

    # Load W2
    for i, v in enumerate(W2.flatten()):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_W2_ARR, S_IDX, S_FTMP)

    # Load b2
    for i, v in enumerate(b2):
        enc.SET(S_IDX, i)
        enc.FSET(S_FTMP, float(v))
        enc.FARR_SET(S_B2_ARR, S_IDX, S_FTMP)

    # Forward pass per sample
    for s_idx, x in enumerate(X_samples):
        # Load input
        for i, v in enumerate(x):
            enc.SET(S_IDX, i)
            enc.FSET(S_FTMP, float(v))
            enc.FARR_SET(S_X_ARR, S_IDX, S_FTMP)

        # Layer 1
        enc.MAT_VEC(S_H_ARR, S_W1_ARR, S_X_ARR, S_N_HIDDEN, S_N_IN)
        enc.VEC_ADD(S_H_ARR, S_H_ARR, S_B1_ARR, S_N_HIDDEN)

        if activation == 'leaky_relu':
            enc.LEAKY_RELU(S_H_ARR, S_N_HIDDEN)
        elif activation == 'tanh':
            for i in range(n_hidden):
                enc.SET(S_IDX, i)
                enc.FARR_GET(S_FTMP, S_H_ARR, S_IDX)
                enc.FTANH(S_FTMP, S_FTMP)
                enc.FARR_SET(S_H_ARR, S_IDX, S_FTMP)

        # Layer 2
        enc.MAT_VEC(S_OUT_ARR, S_W2_ARR, S_H_ARR, S_N_OUT, S_N_HIDDEN)
        enc.VEC_ADD(S_OUT_ARR, S_OUT_ARR, S_B2_ARR, S_N_OUT)

        # Softmax
        enc.SOFTMAX(S_OUT_ARR, S_N_OUT)

        # Argmax
        enc.ARGMAX(S_PRED, S_OUT_ARR, S_N_OUT)

        # Store in result slot 50 + s_idx
        # Use SUB: result_slot = S_PRED - S_ZERO (effectively a copy)
        enc._instrs.append(('CUSTOM', MLEncoder.TOK_SUB, [50 + s_idx, S_PRED, S_ZERO]))

    return enc.build()


if __name__ == '__main__':
    print("Testing encoder...")
    # Tiny test: 2-in, 4-hidden, 2-out
    np.random.seed(42)
    W1t = np.random.randn(4, 2).astype(np.float32) * 0.5
    b1t = np.zeros(4, dtype=np.float32)
    W2t = np.random.randn(2, 4).astype(np.float32) * 0.5
    b2t = np.zeros(2, dtype=np.float32)
    X_t = [np.array([1.0, 0.5], dtype=np.float32)]

    stream = encode_mlp_forward_v2(W1t, b1t, W2t, b2t, X_t, activation='leaky_relu')
    print(f"  Stream size: {len(stream)} bytes")
    print(f"  Hex: {stream[:16].hex()}...")

    # Numpy ground truth
    z1 = X_t[0] @ W1t.T + b1t
    h  = np.where(z1 > 0, z1, 0.01 * z1)
    z2 = h @ W2t.T + b2t
    pred_np = int(np.argmax(z2))
    print(f"  NumPy prediction: {pred_np}")
    print("  (C decoder test will verify this matches)")
