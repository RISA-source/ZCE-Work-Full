"""TEST 2: ACTIVATION MISMATCH SEVERITY on harder data (moons)"""
import sys, math, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import train_model

print("=== ACTIVATION MISMATCH SEVERITY (moons dataset) ===\n")

# Make moons
rng = np.random.RandomState(42); n=300
t0=np.linspace(0,np.pi,n//2); t1=np.linspace(0,np.pi,n//2)
X0=np.c_[np.cos(t0),np.sin(t0)]; X1=np.c_[1-np.cos(t1),1-np.sin(t1)-0.5]
X=np.vstack([X0,X1]).astype(np.float32)+rng.randn(n,2).astype(np.float32)*0.2
X=(X-X.mean(0))/(X.std(0)+1e-8); y=np.array([0]*(n//2)+[1]*(n//2))

act_fns = {
    'leaky_relu': lambda x: max(0.0,x)+0.01*min(0.0,x),
    'swish':      lambda x: x/(1+math.exp(-min(float(x),88))),
    'elu':        lambda x: float(x) if float(x)>=0 else math.exp(float(x))-1,
    'tanh':       math.tanh,
    'relu':       lambda x: max(0.0,x),
    'sine':       math.sin,
}

def np_acc(W1,b1,W2,b2,act_fn,X,y):
    z1=X@W1.T+b1; h=np.vectorize(act_fn)(z1)
    z2=h@W2.T+b2; z2-=z2.max(1,keepdims=True)
    e=np.exp(z2); return float(np.mean(np.argmax(e/e.sum(1,keepdims=True),1)==y))

print("Training 6 models on moons...")
trained={}
for name,fn in act_fns.items():
    w=train_model(name,fn,hidden_size=32,X=X,y=y,epochs=2000,lr=0.1)
    trained[name]=w
    print(f"  {name}: train_acc={w['train_acc']:.3f}")

print(f"\nMismatch matrix (row=trained_with, col=run_with):")
print(f"  {'':>14}", end='')
for n in act_fns: print(f"  {n[:6]:>6}", end='')
print()

worst=[]
for tname in act_fns:
    print(f"  {tname:<14}", end='')
    w=trained[tname]
    correct_acc=None
    for rname,rfn in act_fns.items():
        acc=np_acc(w['W1'],w['b1'],w['W2'],w['b2'],rfn,X,y)
        if rname==tname: correct_acc=acc; marker='●'
        else:
            marker=' '; worst.append((tname,rname,correct_acc or 0,acc,(correct_acc or 0)-acc))
        print(f"  {acc:>5.3f}{marker}", end='')
    print()

worst.sort(key=lambda x:-x[4])
print(f"\n● = correct activation")
print(f"\nTop 3 worst mismatches:")
for t,r,ca,ma,d in worst[:3]:
    print(f"  trained={t} → run_with={r}: {ca:.3f} → {ma:.3f}  drop={d:+.3f}")
print(f"\nMost compatible pairs:")
worst.sort(key=lambda x:abs(x[4]))
for t,r,ca,ma,d in worst[:3]:
    print(f"  trained={t} → run_with={r}: {ca:.3f} → {ma:.3f}  drop={d:+.3f}")
