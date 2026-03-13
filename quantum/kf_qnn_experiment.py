import numpy as np
import pennylane as qml
import warnings; warnings.filterwarnings('ignore')

np.random.seed(42)
n_qubits, n_layers = 4, 2

dev = qml.device("default.qubit", wires=n_qubits)

def make_data(n_tr=60, n_te=150, noise=0.15):
    rng = np.random.RandomState(42)
    def cls(label, n):
        c = np.zeros(n_qubits) if label==0 else np.ones(n_qubits)*np.pi
        X = c + rng.randn(n, n_qubits)*noise*np.pi
        return np.clip(X,-np.pi,np.pi), np.full(n,label)
    n0,n1 = n_tr//2, n_tr-n_tr//2
    Xt = np.vstack([cls(0,n0)[0], cls(1,n1)[0]])
    yt = np.hstack([np.zeros(n0), np.ones(n1)])
    idx = rng.permutation(n_tr); Xt,yt = Xt[idx],yt[idx]
    Xe = np.vstack([cls(0,n_te//2)[0], cls(1,n_te-n_te//2)[0]])
    ye = np.hstack([np.zeros(n_te//2), np.ones(n_te-n_te//2)])
    return Xt,yt,Xe,ye

@qml.qnode(dev)
def circuit(params, x):
    for i in range(n_qubits): qml.RY(x[i], wires=i)
    for l in range(n_layers):
        for i in range(n_qubits): qml.RY(params[l,i,0],wires=i); qml.RZ(params[l,i,1],wires=i)
        for i in range(n_qubits-1): qml.CNOT(wires=[i,i+1])
        qml.CNOT(wires=[n_qubits-1,0])
    return qml.expval(qml.PauliZ(0))

@qml.qnode(dev)
def get_state(params, x):
    for i in range(n_qubits): qml.RY(x[i], wires=i)
    for l in range(n_layers):
        for i in range(n_qubits): qml.RY(params[l,i,0],wires=i); qml.RZ(params[l,i,1],wires=i)
        for i in range(n_qubits-1): qml.CNOT(wires=[i,i+1])
        qml.CNOT(wires=[n_qubits-1,0])
    return qml.state()

def entropy(params, x):
    s = np.array(get_state(params,x)).reshape(4,4)
    sv = np.linalg.svd(s, compute_uv=False)
    p = sv**2; p = p[p>1e-12]
    return float(-np.sum(p*np.log2(p+1e-15)))

def predict(params, X):
    return np.array([float(circuit(params,x)) for x in X])

def ce_loss(params, X, y):
    p = np.clip((predict(params,X)+1)/2, 1e-7, 1-1e-7)
    return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))

def acc(params, X, y):
    return float(np.mean((predict(params,X)>0).astype(int)==y.astype(int)))

def kf_batch(params, X, n=15):
    return float(np.mean([entropy(params,x) for x in X[:n]]))

def train(X_tr,y_tr,X_te,y_te, reg=False, lam=0.5, epochs=40, lr=0.08):
    rng = np.random.RandomState(7)
    params = rng.randn(n_layers,n_qubits,2)*0.1
    hist = {'tr_acc':[],'te_acc':[],'tr_loss':[],'te_loss':[],'kf':[]}
    
    for ep in range(epochs):
        # Finite diff gradient (small params, fast enough for 2 layers)
        grad = np.zeros_like(params)
        eps = 0.05
        for idx in np.ndindex(params.shape):
            p2 = params.copy(); p2[idx]+=eps
            p3 = params.copy(); p3[idx]-=eps
            f2 = ce_loss(p2,X_tr,y_tr); f3 = ce_loss(p3,X_tr,y_tr)
            if reg:
                k2 = kf_batch(p2,X_tr); k3 = kf_batch(p3,X_tr)
                f2 += lam*k2; f3 += lam*k3
            grad[idx] = (f2-f3)/(2*eps)
        params -= lr*grad
        
        kf = kf_batch(params, X_tr)
        tr_l = ce_loss(params,X_tr,y_tr)
        te_l = ce_loss(params,X_te,y_te)
        tr_a = acc(params,X_tr,y_tr)
        te_a = acc(params,X_te,y_te)
        hist['tr_acc'].append(tr_a); hist['te_acc'].append(te_a)
        hist['tr_loss'].append(tr_l); hist['te_loss'].append(te_l)
        hist['kf'].append(kf)
        
        if ep % 10 == 0 or ep == epochs-1:
            label = "KF-reg" if reg else "Std   "
            print(f"    [{label}] ep={ep:2d}  tr={tr_a:.3f}  te={te_a:.3f}  "
                  f"loss={tr_l:.3f}  kf={kf:.3f}")
    return params, hist

print("K_F REGULARIZATION EXPERIMENT")
print("="*50)
X_tr,y_tr,X_te,y_te = make_data()
print(f"Data: {len(X_tr)} train, {len(X_te)} test")
print(f"Model: {n_qubits}q, {n_layers} layers, {n_layers*n_qubits*2} params")

print("\n[1/2] Standard QNN:")
p_std, h_std = train(X_tr,y_tr,X_te,y_te, reg=False, epochs=40)

print("\n[2/2] K_F Regularized QNN (lambda=0.5):")
p_kf,  h_kf  = train(X_tr,y_tr,X_te,y_te, reg=True,  lam=0.5, epochs=40)

print("\n" + "="*50)
print("FINAL RESULTS")
print("="*50)
print(f"\n  {'Metric':<28} {'Standard':>10} {'K_F-reg':>10}")
print("  " + "-"*50)
for label, k in [("Train accuracy","tr_acc"),("Test accuracy","te_acc"),
                  ("Train loss","tr_loss"),("Test loss","te_loss"),("K_F proxy (entropy)","kf")]:
    sv, kv = h_std[k][-1], h_kf[k][-1]
    better = " ✓" if (k in ['te_acc'] and kv>sv) or (k in ['kf','te_loss'] and kv<sv) else ""
    print(f"  {label:<28} {sv:>10.4f} {kv:>10.4f}{better}")

gen_std = h_std['tr_acc'][-1] - h_std['te_acc'][-1]
gen_kf  = h_kf['tr_acc'][-1]  - h_kf['te_acc'][-1]
print(f"  {'Generalization gap':<28} {gen_std:>10.4f} {gen_kf:>10.4f}"
      + (" ✓" if gen_kf < gen_std else ""))

kf_std = h_std['kf'][-1]; kf_kfr = h_kf['kf'][-1]
print()
print(f"  K_F proxy reduced by: {kf_std-kf_kfr:.3f} bits")
print(f"  Classical sim cost: {2**kf_std:.1f}x → {2**kf_kfr:.1f}x")
print(f"  Speedup: {2**kf_std/2**kf_kfr:.2f}x easier to simulate classically")
