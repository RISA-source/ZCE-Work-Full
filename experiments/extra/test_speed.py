"""TEST 1: SPEED — ZCE VM vs raw NumPy"""
import sys, time, math, numpy as np
sys.path.insert(0, '/home/claude')
from zce_arch_test import GenericVM, encode, decode, make_leaky_relu_1input, train_model, export_model

print("=== SPEED BENCHMARK ===\n")

# Train a model
leaky_fn = lambda x: max(0.0,x) + 0.01*min(0.0,x)
print("Training model...")
w = train_model('leaky_relu', leaky_fn, hidden_size=16)
W1,b1,W2,b2 = w['W1'],w['b1'],w['W2'],w['b2']

# NumPy forward pass
def np_forward(x):
    z1 = x @ W1.T + b1
    h  = np.where(z1>0, z1, 0.01*z1)
    z2 = h @ W2.T + b2
    z2 -= z2.max(); e=np.exp(z2); return np.argmax(e/e.sum())

# ZCE bitstream
op_def = make_leaky_relu_1input(0.01)
bc, fs = export_model(w, op_def)

x_test = w['X_sample'][0:1]
N = 30

# Warm up
for _ in range(3): np_forward(x_test)
vm=GenericVM(); vm.run(bc, fs)

# Time NumPy
t0=time.perf_counter()
for _ in range(N): np_forward(x_test)
t_np = (time.perf_counter()-t0)/N*1000

# Time ZCE full (decode + execute)
t0=time.perf_counter()
for _ in range(N):
    vm=GenericVM(); vm.run(bc, fs)
t_zce_full = (time.perf_counter()-t0)/N*1000

# Time ZCE decode only
t0=time.perf_counter()
for _ in range(N): ops,data=decode(bc,fs)
t_decode = (time.perf_counter()-t0)/N*1000

t_execute = max(t_zce_full - t_decode, 0.0001)

print(f"\nBitstream size:    {len(bc)//8} bytes")
print(f"NumPy model bytes: {W1.nbytes+b1.nbytes+W2.nbytes+b2.nbytes}")
print(f"\n{'Operation':<35} {'ms/call':>10} {'vs NumPy':>10}")
print(f"{'-'*55}")
print(f"{'NumPy single sample':<35} {t_np:>10.3f} {'1.0x':>10}")
print(f"{'ZCE full (decode+execute)':<35} {t_zce_full:>10.3f} {t_zce_full/t_np:>9.0f}x")
print(f"{'ZCE decode only':<35} {t_decode:>10.3f} {t_decode/t_np:>9.0f}x")
print(f"{'ZCE execute only (est)':<35} {t_execute:>10.3f} {t_execute/t_np:>9.0f}x")
print(f"\nOverhead: {t_zce_full/t_np:.0f}x slower than NumPy")
print(f"Decode is {t_decode/t_zce_full*100:.0f}% of total ZCE time")
print(f"\nNote: This is Python VM vs compiled BLAS.")
print(f"A C/Rust ZCE runtime would close most of this gap.")
print(f"Cached decode (amortized): ~{t_execute:.3f}ms per inference")
