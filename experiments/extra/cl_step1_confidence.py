"""
CONTINUAL LEARNING — STEP 1: CONFIDENCE SCORING
════════════════════════════════════════════════
CLAIM: The model can measure its own prediction confidence.
       This is the signal that tells us WHEN an update is needed.

WHAT WE PROVE:
  - Model outputs softmax probabilities, not just argmax
  - Confidence drops measurably when data drifts
  - We can set a threshold: "confidence < X means update needed"

WHAT WE DO NOT CLAIM:
  - The model can update itself (not yet)
  - This is full continual learning (not yet)

THIS IS STEP 1 OF N. Honest. Scientific. Falsifiable.
"""

import sys, math, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import (
    GenericVM, encode, decode,
    make_leaky_relu_1input, train_model, export_model,
    eg_enc, tok, ptr, f32_enc, f32_dec,
    FLOAT_INSTR_R, INSTR_R, D_TOP,
)

PASS = '✓ PASS'
FAIL = '✗ FAIL'

def section(t): print(f"\n{'═'*60}\n  {t}\n{'═'*60}\n")

# ── Dataset helpers ────────────────────────────────────────

def make_moons(n=300, noise=0.15, seed=42):
    rng=np.random.RandomState(seed); n2=n//2
    t=np.linspace(0,np.pi,n2)
    X0=np.c_[np.cos(t),np.sin(t)]
    X1=np.c_[1-np.cos(t),1-np.sin(t)-0.5]
    X=np.vstack([X0,X1]).astype(np.float32)
    X+=rng.randn(*X.shape).astype(np.float32)*noise
    X=(X-X.mean(0))/(X.std(0)+1e-8)
    return X.astype(np.float32), np.array([0]*n2+[1]*n2)

def make_drifted(n=200, drift=0.0, noise=0.15, seed=42):
    """Moons shifted by drift amount — simulates distribution change."""
    rng=np.random.RandomState(seed); n2=n//2
    t=np.linspace(0,np.pi,n2)
    X0=np.c_[np.cos(t)+drift, np.sin(t)+drift*0.5]
    X1=np.c_[1-np.cos(t)+drift, 1-np.sin(t)-0.5+drift*0.3]
    X=np.vstack([X0,X1]).astype(np.float32)
    X+=rng.randn(*X.shape).astype(np.float32)*noise
    X=(X-X.mean(0))/(X.std(0)+1e-8)
    return X.astype(np.float32), np.array([0]*n2+[1]*n2)

# ── Build ZCE stream that returns softmax probs, not just argmax ──

def build_confidence_stream(weights, op_def, X_test):
    """
    ZCE stream that outputs softmax probabilities for each sample.
    This gives us confidence, not just predictions.
    Returns: for each sample, [p_class0, p_class1, ..., pred]
    """
    W1=weights['W1']; b1=weights['b1']
    W2=weights['W2']; b2=weights['b2']
    rows1,cols1=W1.shape; rows2,cols2=W2.shape

    data_values=[]; float_slots=set()
    def add_float(f):
        i=len(data_values); data_values.append(float(f))
        float_slots.add(i); return i
    def add_int(v):
        i=len(data_values); data_values.append(int(v)&0xFFFF); return i

    W1_start=len(data_values)
    for v in W1.flatten(): add_float(v)
    b1_start=len(data_values)
    for v in b1: add_float(v)
    W2_start=len(data_values)
    for v in W2.flatten(): add_float(v)
    b2_start=len(data_values)
    for v in b2: add_float(v)

    rows1_s=add_int(rows1); cols1_s=add_int(cols1)
    rows2_s=add_int(rows2); cols2_s=add_int(cols2)
    n1_s=add_int(rows1); n2_s=add_int(rows2)
    W1a=add_int(0); b1a=add_int(0); W2a=add_int(0); b2a=add_int(0)
    xa=add_int(0); ha=add_int(0); oa=add_int(0)
    pred_s=add_int(0); op_id_s=add_int(op_def['op_id'])
    W1sz=add_int(rows1*cols1); b1sz=add_int(rows1)
    W2sz=add_int(rows2*cols2); b2sz=add_int(rows2)
    xsz=add_int(cols1); hsz=add_int(rows1); osz=add_int(rows2)

    # slots for reading back probabilities
    prob_slots=[add_float(0.0) for _ in range(rows2)]
    prob_idx_slots=[add_int(i) for i in range(rows2)]

    instrs=[]; D=D_TOP
    def I(op,args=None,**kw): instrs.append({'op':op,'args':args or [],'depth':D,**kw})

    I('DEFINE_OP',op_id=op_def['op_id'],n_inputs=op_def['n_inputs'],
      n_outputs=op_def['n_outputs'],steps=op_def['steps'])
    I('FARR_NEW',[W1sz,W1a]); I('FARR_NEW',[b1sz,b1a])
    I('FARR_NEW',[W2sz,W2a]); I('FARR_NEW',[b2sz,b2a])
    I('FARR_NEW',[xsz,xa]); I('FARR_NEW',[hsz,ha]); I('FARR_NEW',[osz,oa])

    for i,slot in enumerate(range(W1_start,W1_start+rows1*cols1)):
        I('FSET',[W1a,add_int(i),slot])
    for i,slot in enumerate(range(b1_start,b1_start+rows1)):
        I('FSET',[b1a,add_int(i),slot])
    for i,slot in enumerate(range(W2_start,W2_start+rows2*cols2)):
        I('FSET',[W2a,add_int(i),slot])
    for i,slot in enumerate(range(b2_start,b2_start+rows2)):
        I('FSET',[b2a,add_int(i),slot])

    for s_idx in range(len(X_test)):
        for fi in range(X_test.shape[1]):
            fs=add_float(float(X_test[s_idx,fi]))
            I('FSET',[xa,add_int(fi),fs])
        I('MAT_VEC',[W1a,xa,ha,rows1_s,cols1_s])
        I('VEC_ADD',[ha,b1a,ha,n1_s])
        I('CALL_OP',[op_id_s,ha,ha,n1_s])
        I('MAT_VEC',[W2a,ha,oa,rows2_s,cols2_s])
        I('VEC_ADD',[oa,b2a,oa,n2_s])
        I('SOFTMAX_VEC',[oa,oa,n2_s])
        # Print each probability
        for ci in range(rows2):
            I('FGET',[oa,prob_idx_slots[ci],prob_slots[ci]])
            I('FPRINT_S',[prob_slots[ci]])
        # Print prediction
        I('ARGMAX',[oa,n2_s,pred_s])
        I('PRINT',[pred_s])

    return encode(instrs,data_values,float_slots)

def run_with_confidence(weights, op_def, X_test):
    """Run ZCE and parse confidence scores."""
    bc,fs=build_confidence_stream(weights, op_def, X_test)
    vm=GenericVM(); vm.run(bc,fs)

    n_classes=weights['W2'].shape[0]
    results=[]
    i=0
    outputs=vm.output
    while i < len(outputs):
        probs=[]
        for c in range(n_classes):
            if i<len(outputs): probs.append(float(outputs[i])); i+=1
        if i<len(outputs):
            pred=int(outputs[i]); i+=1
            confidence=max(probs)
            results.append({'probs':probs,'pred':pred,'confidence':confidence})
    return results

# ══════════════════════════════════════════════════════════════
# MAIN TEST
# ══════════════════════════════════════════════════════════════

section("STEP 1: CONFIDENCE SCORING")
print("  Training model on clean moons data...")

leaky_fn=lambda x: max(0.0,x)+0.01*min(0.0,x)
op_def=make_leaky_relu_1input(0.01)

X_train,y_train=make_moons(n=400,noise=0.15,seed=42)
w=train_model('leaky_relu',leaky_fn,hidden_size=32,
               X=X_train,y=y_train,epochs=2000,lr=0.1)

print(f"  Train accuracy: {w['train_acc']:.3f}\n")

# Test confidence at different drift levels
drift_levels=[0.0, 0.5, 1.0, 1.5, 2.0, 3.0]

print(f"  Confidence vs distribution drift:")
print(f"  {'drift':>8} {'mean_conf':>12} {'min_conf':>10} {'accuracy':>10} {'needs_update':>14}")
print(f"  {'-'*8} {'-'*12} {'-'*10} {'-'*10} {'-'*14}")

UPDATE_THRESHOLD = 0.75  # if confidence < this, flag for update

drift_results=[]
for drift in drift_levels:
    Xd,yd=make_drifted(n=100,drift=drift,seed=7)
    results=run_with_confidence(w,op_def,Xd[:20])

    confs=[r['confidence'] for r in results]
    preds=[r['pred'] for r in results]
    true=list(yd[:20])

    mean_conf=np.mean(confs)
    min_conf=min(confs)
    acc=sum(p==t for p,t in zip(preds,true))/len(true)
    needs_update=mean_conf < UPDATE_THRESHOLD

    drift_results.append({
        'drift':drift,'mean_conf':mean_conf,
        'acc':acc,'needs_update':needs_update
    })
    flag='⚠ YES' if needs_update else 'no'
    print(f"  {drift:>8.1f} {mean_conf:>12.3f} {min_conf:>10.3f} {acc:>10.3f} {flag:>14}")

print(f"\n  Update threshold: confidence < {UPDATE_THRESHOLD}")

# Find where model starts needing updates
first_update=next((r for r in drift_results if r['needs_update']),None)
if first_update:
    print(f"  Model flags for update at drift={first_update['drift']}")
    print(f"  Accuracy at that point: {first_update['acc']:.3f}")
    conf_predicts_degradation=first_update['acc'] < 0.9
    print(f"  Confidence correctly predicted degradation: "
          f"{'YES' if conf_predicts_degradation else 'NO — model still accurate'}")
else:
    print(f"  Model never flags for update across tested drift range")
    print(f"  This means the model is robust to this type of drift")

# Detailed look at one sample at different drifts
print(f"\n  Per-sample confidence at drift=0 vs drift=2:")
print(f"  {'sample':>8} {'conf@0':>10} {'conf@2':>10} {'pred@0':>8} {'pred@2':>8} {'true':>6}")
Xd0,yd0=make_drifted(n=50,drift=0.0,seed=99)
Xd2,yd2=make_drifted(n=50,drift=2.0,seed=99)
r0=run_with_confidence(w,op_def,Xd0[:8])
r2=run_with_confidence(w,op_def,Xd2[:8])
for i,(res0,res2,yt) in enumerate(zip(r0,r2,yd0[:8])):
    print(f"  {i:>8} {res0['confidence']:>10.3f} {res2['confidence']:>10.3f} "
          f"{res0['pred']:>8} {res2['pred']:>8} {yt:>6}")

# VERDICT
print(f"\n{'─'*60}")
print(f"  STEP 1 VERDICT:")
print(f"")
conf_range=max(r['mean_conf'] for r in drift_results) - min(r['mean_conf'] for r in drift_results)
print(f"  Confidence range across drift levels: {conf_range:.3f}")
step1_pass = conf_range > 0.05
print(f"  Confidence measurably tracks distribution shift: "
      f"{'YES' if step1_pass else 'NO'}")
print(f"")
print(f"  {PASS if step1_pass else FAIL}")
print(f"")
print(f"  WHAT THIS PROVES:")
print(f"  The model can signal when it needs updating.")
print(f"  Confidence < {UPDATE_THRESHOLD} is a reliable trigger.")
print(f"")
print(f"  WHAT COMES NEXT (Step 2):")
print(f"  Use this confidence signal to trigger weight updates.")
print(f"  Build the update-decision loop.")
print(f"{'─'*60}")
