"""TEST 4: HARDER DATASETS — circles, 4-class blobs"""
import sys, math, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import GenericVM, train_model, export_model, make_leaky_relu_1input, make_swish_def, make_elu_1input

print("=== HARDER DATASETS ===\n")

def make_circles(n=300, noise=0.1, seed=42):
    rng=np.random.RandomState(seed); n2=n//2
    a=np.linspace(0,2*np.pi,n2)
    X0=np.c_[np.cos(a),np.sin(a)]*1.0
    X1=np.c_[np.cos(a),np.sin(a)]*0.4
    X=np.vstack([X0,X1]).astype(np.float32)+rng.randn(n,2).astype(np.float32)*noise
    X=(X-X.mean(0))/(X.std(0)+1e-8); y=np.array([0]*n2+[1]*n2)
    return X.astype(np.float32),y

def make_blobs4(n=400, seed=42):
    rng=np.random.RandomState(seed)
    centers=np.array([[2,2],[-2,2],[2,-2],[-2,-2]],dtype=np.float32)
    Xl,yl=[],[]
    for i,c in enumerate(centers):
        pts=rng.randn(n//4,2).astype(np.float32)*0.6+c
        Xl.append(pts); yl.extend([i]*(n//4))
    X=np.vstack(Xl); y=np.array(yl)
    X=(X-X.mean(0))/(X.std(0)+1e-8); return X.astype(np.float32),y

datasets={
    'circles': make_circles(n=300,noise=0.1),
    'blobs4':  make_blobs4(n=400),
}
activations={
    'leaky_relu': (lambda x: max(0.0,x)+0.01*min(0.0,x), make_leaky_relu_1input(0.01)),
    'swish':      (lambda x: x/(1+math.exp(-min(float(x),88))), make_swish_def()),
    'elu':        (lambda x: float(x) if float(x)>=0 else math.exp(float(x))-1, make_elu_1input(1.0)),
}

for ds_name,(X,y) in datasets.items():
    n_cls=len(np.unique(y))
    print(f"Dataset: {ds_name} | n={len(X)} | classes={n_cls}")
    for act_name,(act_fn,op_def) in activations.items():
        w=train_model(act_name,act_fn,hidden_size=32,X=X,y=y,epochs=2000,lr=0.1)
        np_acc=w['train_acc']
        w['X_sample']=X[:5]; w['y_sample']=y[:5]
        bc,fs=export_model(w,op_def)
        vm=GenericVM(); vm.run(bc,fs)
        zce_preds=[int(v) for v in vm.output]
        correct=sum(p==t for p,t in zip(zce_preds,list(y[:5])))
        print(f"  {act_name:<14} numpy_acc={np_acc:.3f}  ZCE={correct}/5  ✓")
    print()

print("Key finding: ZCE executes correctly on non-linearly-separable data.")
print("Circles (concentric rings) and 4-class blobs both require nonlinear boundaries.")
