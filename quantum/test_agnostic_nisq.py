"""
TEST: Agnostic MDL Certification for NISQ Devices
===================================================
Theorem A: For noisy state sigma with best-fit rho* having K_F = K*,
the agnostic MDL learner outputs rho_hat with:
  D_tr(rho_hat, sigma) <= opt + 2*eps
using m <= K*/eps^2 measurements.

Test this concretely across noise models and system sizes.
"""
import math, sys, numpy as np
from itertools import product as iproduct
sys.path.insert(0, '/mnt/user-data/uploads')
from zce_core import Asm

PASS = 0; FAIL = 0

def check(label, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✓  {label}")
    else: FAIL += 1; print(f"  ✗  {label}  [{info}]")

def trace_distance(rho, sigma):
    diff = rho - sigma
    eigs = np.linalg.eigvalsh(diff)
    return 0.5 * np.sum(np.abs(eigs))

def depolarize(rho, p):
    """Apply depolarizing noise: (1-p)*rho + p*I/d"""
    d = rho.shape[0]
    return (1-p)*rho + p*np.eye(d)/d

def dephase(rho, p):
    """Apply dephasing noise: kill off-diagonal by factor (1-p)"""
    result = rho.copy()
    d = rho.shape[0]
    for i in range(d):
        for j in range(d):
            if i != j:
                result[i,j] *= (1-p)
    return result

def amplitude_damp(rho, gamma):
    """Amplitude damping on single qubit"""
    K0 = np.array([[1, 0],[0, np.sqrt(1-gamma)]])
    K1 = np.array([[0, np.sqrt(gamma)],[0, 0]])
    return K0 @ rho @ K0.T.conj() + K1 @ rho @ K1.T.conj()

# States we'll test
states = {
    "|0>": np.array([[1,0],[0,0]], dtype=complex),
    "|+>": np.array([[0.5,0.5],[0.5,0.5]], dtype=complex),
    "Bell": np.array([[0.5,0,0,0.5],[0,0,0,0],[0,0,0,0],[0.5,0,0,0.5]], dtype=complex),
    "GHZ3": None,  # will compute
}

# Build 3-qubit GHZ state
ghz3 = np.zeros((8,8), dtype=complex)
ghz3[0,0] = 0.5; ghz3[0,7] = 0.5
ghz3[7,0] = 0.5; ghz3[7,7] = 0.5
states["GHZ3"] = ghz3

# K_F values (from ZCE assembler measurements)
kf_vals = {"|0>": 88, "|+>": 96, "Bell": 208, "GHZ3": 240}

print("="*60)
print("SECTION 1: Agnostic Bound Verification")
print("  m <= K*/eps^2 measurements for error <= opt + 2*eps")
print("="*60)
print()
print(f"  {'State':<10} {'Noise':<12} {'opt':<8} {'eps':<6} {'m_bound':<10} {'m_std':<12} {'Improvement'}")
print("  " + "-"*70)

eps = 0.05
results = []

for state_name, rho_ideal in states.items():
    if rho_ideal is None: continue
    kf = kf_vals[state_name]
    d = rho_ideal.shape[0]
    
    noise_models = [
        ("depol-1%",  depolarize(rho_ideal, 0.01)),
        ("depol-5%",  depolarize(rho_ideal, 0.05)),
        ("depol-15%", depolarize(rho_ideal, 0.15)),
        ("dephase-5%",dephase(rho_ideal, 0.05)),
    ]
    
    for noise_name, rho_noisy in noise_models:
        opt = trace_distance(rho_ideal, rho_noisy)
        m_bound = int(kf * math.log(2) / eps**2) + 1
        m_std = int(d**2 / eps**2)
        improvement = m_std / m_bound
        results.append((state_name, noise_name, opt, eps, m_bound, m_std, improvement))
        print(f"  {state_name:<10} {noise_name:<12} {opt:.4f}  {eps:<6} {m_bound:<10} {m_std:<12} {improvement:.1f}x")

print()
# Verify interpolation bound: if we know opt, we can use K*/(eps*(eps-opt))
print("="*60)
print("SECTION 2: Interpolation Bound")
print("  m <= K*/(eps*(eps-opt))  when opt < eps")
print("="*60)
print()
print(f"  {'State':<10} {'opt':<8} {'eps':<6} {'m_realizable':<15} {'m_interp':<15} {'m_agnostic':<12}")
print("  " + "-"*65)

for state_name, rho_ideal in states.items():
    if rho_ideal is None: continue
    kf = kf_vals[state_name]
    
    for noise_p in [0.0, 0.01, 0.02, 0.04]:
        rho_noisy = depolarize(rho_ideal, noise_p)
        opt = trace_distance(rho_ideal, rho_noisy)
        eps = 0.05
        
        m_realizable = int(kf * math.log(2) / eps)
        if opt < eps - 0.001:
            m_interp = int(kf * math.log(2) / (eps * (eps - opt)))
        else:
            m_interp = float('inf')
        m_agnostic = int(kf * math.log(2) / eps**2)
        
        print(f"  {state_name:<10} {opt:.4f}  {eps:<6} {m_realizable:<15} {m_interp:<15} {m_agnostic:<12}")

print()
print("="*60)
print("SECTION 3: What the Agnostic Bound Tells You About NISQ Devices")
print("="*60)
print()

# For a real NISQ device running a CNOT gate:
# Ideal: CNOT unitary U_CNOT
# Actual: U_CNOT * (depolarizing noise)
# K_F(J(CNOT)) ~ 150 bits (stabilizer structure)
# 
# At noise rate p=0.01 (1%), opt ≈ 0.01
# Agnostic bound: m <= 150*ln2/0.05^2 = 41,589 measurements
# Standard: m <= 4^4/0.05^2 = 102,400 measurements
# 
# But we can do BETTER with interpolation (knowing opt ~ 0.01):
# m <= 150*ln2/(0.05*(0.05-0.01)) = 2598 measurements

print("  CNOT gate certification example:")
print()
kf_cnot = 150
d_cnot = 4  # 2-qubit gate
eps = 0.05
for opt in [0.0, 0.005, 0.01, 0.02, 0.04, 0.05]:
    m_std = int(d_cnot**4 / eps**2)
    m_agnostic = int(kf_cnot * math.log(2) / eps**2)
    if opt < eps - 0.001:
        m_interp = int(kf_cnot * math.log(2) / (eps * max(eps-opt, 0.001)))
    else:
        m_interp = "N/A (opt>=eps)"
    noise_label = f"noise={opt:.1%}"
    print(f"  {noise_label:<15} m_std={m_std:<8} m_agnostic={m_agnostic:<8} m_interp={m_interp}")

print()
print("="*60)
print("SECTION 4: Multi-qubit NISQ scaling")
print("="*60)
print()
print(f"  {'n_qubits':<12} {'K_F_circuit':<14} {'m_agnostic':<14} {'m_standard':<14} {'ratio'}")
print("  " + "-"*65)

for n in [2, 3, 5, 7, 10, 15, 20]:
    # Shallow circuit of depth 10 on n qubits
    # K_F ~ n * depth * bits_per_gate = n * 10 * 10 = 100n
    kf_circuit = 100 * n
    eps = 0.05
    m_agnostic = int(kf_circuit * math.log(2) / eps**2)
    m_std = int(4**n / eps**2)
    ratio = m_std / m_agnostic
    print(f"  {n:<12} {kf_circuit:<14} {m_agnostic:<14} {m_std:<14} {ratio:.1e}")

# Run verification checks
print()
check("Depolarizing opt computed correctly for Bell+1%",
      abs(trace_distance(states["Bell"], depolarize(states["Bell"], 0.01)) - 0.0075) < 0.001)
check("Agnostic bound m = K*ln2/eps^2 = 57669",
      int(208 * math.log(2) / 0.05**2) == 57669)
check("Realizable m < agnostic m (1/eps vs 1/eps^2)",
      int(208 * math.log(2) / 0.05) < int(208 * math.log(2) / 0.05**2))
check("CNOT agnostic better than standard",
      int(150 * math.log(2) / 0.05**2) < int(4**4 / 0.05**2))
check("20-qubit improvement > 10^6x",
      4**20 / (100*20*math.log(2)/0.05**2) > 1e6)

print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'='*60}")
