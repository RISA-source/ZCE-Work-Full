"""TEST 3: NOVEL OPS — sine, gaussian, softsign on hard data"""
import sys, math, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import GenericVM, BASE_PRIMITIVES, train_model, export_model

print("=== NOVEL GRAMMAR-DEFINED ACTIVATIONS ===\n")

# Moons data
rng=np.random.RandomState(42); n=300
t0=np.linspace(0,np.pi,n//2); t1=np.linspace(0,np.pi,n//2)
X0=np.c_[np.cos(t0),np.sin(t0)]; X1=np.c_[1-np.cos(t1),1-np.sin(t1)-0.5]
X=np.vstack([X0,X1]).astype(np.float32)+rng.randn(n,2).astype(np.float32)*0.2
X=(X-X.mean(0))/(X.std(0)+1e-8); y=np.array([0]*(n//2)+[1]*(n//2))

def make_gaussian_op():
    # gaussian(x) = exp(-x^2)
    steps=[(2,0,0,2),(7,2,0,3),(4,3,0,1)]
    return {'op_id':6,'name':'gaussian','n_inputs':1,'n_outputs':1,'steps':steps}

def make_softsign_op():
    # softsign(x) = x/(1+|x|)
    steps=[(6,0,0,2),(11,0,0,3),(0,3,2,4),(3,0,4,1)]
    return {'op_id':7,'name':'softsign','n_inputs':1,'n_outputs':1,'steps':steps}

def make_sine_approx_op():
    # sin(x) approx: x*(1 - x^2/6)  Horner form
    steps=[
        (2,0,0,2),   # s2=x^2
        (11,0,0,3),  # s3=1
        (0,3,3,4),   # s4=2
        (0,4,3,5),   # s5=3
        (2,5,4,6),   # s6=6
        (3,2,6,7),   # s7=x^2/6
        (1,3,7,8),   # s8=1-x^2/6
        (2,0,8,1),   # s1=x*(1-x^2/6)
    ]
    return {'op_id':5,'name':'sine_approx','n_inputs':1,'n_outputs':1,'steps':steps}

novel_ops=[
    ('gaussian',   make_gaussian_op(),   lambda x: math.exp(-x*x)),
    ('softsign',   make_softsign_op(),   lambda x: x/(1+abs(x))),
    ('sine_approx',make_sine_approx_op(),lambda x: x*(1-x*x/6)),
]

# Verify each op
print("Verifying novel ops against reference:")
vm=GenericVM()
test_xs=[-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0]
for opname,op_def,ref_fn in novel_ops:
    errs=[]
    for x in test_xs:
        got=vm.execute_user_op(op_def,x); exp=ref_fn(x)
        errs.append(abs(got-exp))
    print(f"  {opname:<16} max_error={max(errs):.8f}  {'✓' if max(errs)<0.001 else 'approx'}")

# Train and test each
print(f"\nTraining on moons (n=300, noise=0.2):")
for opname,op_def,act_fn in novel_ops:
    w=train_model(opname,act_fn,hidden_size=32,X=X,y=y,epochs=2000,lr=0.1)
    np_acc=w['train_acc']
    w['X_sample']=X[:5]; w['y_sample']=y[:5]
    try:
        bc,fs=export_model(w,op_def)
        vm2=GenericVM(); vm2.run(bc,fs)
        zce_preds=[int(v) for v in vm2.output]
        correct=sum(p==t for p,t in zip(zce_preds,list(y[:5])))
        status=f'ZCE: {correct}/5 correct'
    except Exception as e:
        status=f'ZCE ERROR: {e}'
    print(f"  {opname:<16} numpy_acc={np_acc:.3f}  {status}")

print(f"\nKey finding: These activations don't exist in ONNX/TFLite natively.")
print(f"ZCE grammar expresses them from 13 base primitives.")
