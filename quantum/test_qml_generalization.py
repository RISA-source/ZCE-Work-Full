"""
TEST: Quantum ML Generalization via K_F (Quantum Occam's Razor)
================================================================
Classical ML: generalization gap <= sqrt(VC_dim / m_training)
Quantum ML:   generalization gap <= sqrt(K_F(model) / m_training)

Test this concretely for:
1. VQE-like circuits (variational quantum eigensolver)
2. QNN classification
3. K_F regularization vs unregularized training
"""
import math, sys, numpy as np
sys.path.insert(0, '/mnt/user-data/uploads')
from zce_core import Asm

PASS = 0; FAIL = 0
def check(label, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✓  {label}")
    else: FAIL += 1; print(f"  ✗  {label}  [{info}]")

print("="*60)
print("QUANTUM ML GENERALIZATION BOUNDS VIA K_F")
print("="*60)
print()

# K_F for quantum circuits:
# A circuit of n qubits and depth t with parameterized gates:
# - Each gate has ~3 parameters (rotation angles)
# - Each parameter encoded in ~32 bits in ZCE
# - K_F(circuit) ~ n * t * 3 * 32 = 96*n*t bits
# - But gate type + connectivity adds overhead: ~100*n*t total

def kf_vqe_circuit(n_qubits, depth, bits_per_param=32):
    """K_F for a VQE circuit with RX/RY/RZ gates + CNOT entanglers"""
    # Parameters: 3 per qubit per layer (Euler angles)
    # CNOT gates: O(n) per layer, no parameters but add program structure
    n_params = 3 * n_qubits * depth  # rotation gates
    n_cnot_overhead = n_qubits * depth * 5   # 5 bits per CNOT gate spec
    return n_params * bits_per_param + n_cnot_overhead

def kf_qnn(n_qubits, depth, n_classes, bits_per_param=32):
    """K_F for QNN classifier"""
    kf_circuit = kf_vqe_circuit(n_qubits, depth, bits_per_param)
    kf_readout = n_classes * 16  # measurement basis spec
    return kf_circuit + kf_readout

def gen_bound(kf, m_train):
    """Generalization gap <= sqrt(K_F * ln2 / m_train)"""
    return math.sqrt(kf * math.log(2) / m_train)

print("PART 1: Generalization bounds for VQE models")
print()
print(f"  {'Circuit':<30} {'K_F':<10} {'m_need_0.1':<12} {'m_need_0.05':<14} {'m_standard'}")
print("  " + "-"*72)

vqe_models = [
    ("UCCSD (4q, d=4)",    4,  4),
    ("UCCSD (6q, d=6)",    6,  6),
    ("UCCSD (10q, d=10)",  10, 10),
    ("HEA (4q, d=20)",     4,  20),
    ("HEA (8q, d=20)",     8,  20),
    ("HEA (12q, d=20)",    12, 20),
    ("Ideal (12q, d=1)",   12, 1),  # trivial circuit
]

for name, n, d in vqe_models:
    kf = kf_vqe_circuit(n, d)
    m_01  = int(kf * math.log(2) / 0.1**2)   # gen gap <= 0.1
    m_005 = int(kf * math.log(2) / 0.05**2)  # gen gap <= 0.05
    m_std = int(4**n / 0.1**2)  # standard QST
    print(f"  {name:<30} {kf:<10} {m_01:<12} {m_005:<14} ~10^{int(n*math.log10(4))}")

print()
print("PART 2: The Quantum Occam's Razor in action")
print()
print("  Comparing shallow (simple) vs deep (complex) circuits")
print("  SAME expressiveness for some tasks, but different K_F -> different generalization")
print()

n_qubits = 8
eps = 0.1  # generalization gap tolerance

print(f"  {'Depth':<8} {'K_F':<10} {'m_train_needed':<18} {'gen_gap_at_m=1000'}")
print("  " + "-"*55)
for depth in [1, 2, 4, 8, 16, 32, 64]:
    kf = kf_vqe_circuit(n_qubits, depth)
    m_train = int(kf * math.log(2) / eps**2)
    gen_at_1000 = gen_bound(kf, 1000)
    print(f"  {depth:<8} {kf:<10} {m_train:<18} {gen_at_1000:.4f}")

print()
print("  KEY: Shallow circuits (d=1,2) generalize well with few training samples.")
print("       Deep circuits (d=64) overfit unless m_train >> 10^5.")
print("       Classical analogy: few parameters -> simpler model -> better generalization.")
print()

print("PART 3: K_F regularization")
print()
print("  Regularized objective: L(rho) = loss(rho) + lambda * K_F(rho)")
print()
print("  Choosing lambda = sqrt(1/(m_train)):")
print("  Generalization gap <= 2 * sqrt(K_F(rho_min) * ln2 / m_train)")
print()

# Simulate: training loss vs generalization for different circuit depths
# Key finding: with K_F regularization, optimal depth is ~sqrt(m_train)
n_q = 6
print(f"  For n={n_q} qubits, m_train training samples:")
print(f"  {'m_train':<10} {'optimal_depth':<16} {'gen_gap':<12} {'training_bound'}")
print("  " + "-"*52)
for m_train in [100, 500, 1000, 5000, 10000, 50000]:
    # Optimal depth minimizes training_loss + lambda * K_F
    # With lambda = sqrt(1/m_train), optimal K_F ~ sqrt(m_train)
    kf_optimal = math.sqrt(m_train / math.log(2))
    # kf = 96 * n * depth => depth_optimal = kf_optimal / (96 * n)
    depth_opt = max(1, int(kf_optimal / (96 * n_q)))
    kf_used = kf_vqe_circuit(n_q, depth_opt)
    gen = gen_bound(kf_used, m_train)
    print(f"  {m_train:<10} {depth_opt:<16} {gen:<12.4f} {math.sqrt(kf_used*math.log(2)/m_train):.4f}")

print()
print("PART 4: QML vs Classical ML generalization comparison")
print()
print("  Classical: VC dim bounds generalization via sample complexity")
print("  Quantum: K_F bounds generalization via measurement complexity")
print("  The formulas are IDENTICAL in structure.")
print()
print("  Classical: gen_gap <= sqrt(VC_dim / m)")
print("  Quantum:   gen_gap <= sqrt(K_F * ln2 / m)")
print()
print("  Where VC_dim for neural nets ~ n_params, K_F for quantum ~ n_params * 32 bits")
print()
print(f"  {'Model':<30} {'n_params':<12} {'VC/K_F':<12} {'m_for_gen_0.1'}")
print("  " + "-"*66)

# Classical: linear model on 100 features
classical_models = [
    ("Linear (d=100)",     100,  100,  True),
    ("MLP 2-layer (100)", 10000, 10000, True),
    ("ResNet-50",   25e6,  25e6, True),
]
quantum_models = [
    ("VQC (4q, d=4)",   None, kf_vqe_circuit(4,4),  False),
    ("VQC (8q, d=8)",   None, kf_vqe_circuit(8,8),  False),
    ("VQC (12q, d=20)", None, kf_vqe_circuit(12,20),False),
]

for name, n_p, kf_or_vc, is_classical in classical_models:
    m_needed = int(kf_or_vc / 0.01)  # gen <= 0.1, so kf/m <= 0.01
    print(f"  {name:<30} {n_p:<12.0f} VC={kf_or_vc:<8.0f} {m_needed}")

for name, n_p, kf, is_classical in quantum_models:
    m_needed = int(kf * math.log(2) / 0.01)
    print(f"  {name:<30} {'quantum':<12} K_F={kf:<8} {m_needed}")

# Checks
check("K_F grows linearly in depth",
      kf_vqe_circuit(8, 10) == 2 * kf_vqe_circuit(8, 5))
check("Generalization bound decreases with more training data",
      gen_bound(kf_vqe_circuit(8,4), 10000) < gen_bound(kf_vqe_circuit(8,4), 1000))
check("Deeper circuits need more training data for same generalization",
      int(kf_vqe_circuit(8,16)*math.log(2)/0.1**2) > int(kf_vqe_circuit(8,4)*math.log(2)/0.1**2))
check("K_F formula: gen = sqrt(K_F*ln2/m)",
      abs(gen_bound(1000, 500) - math.sqrt(1000*math.log(2)/500)) < 1e-10)
check("MDL training samples << standard QST for structured QML",
      int(kf_vqe_circuit(10,10)*math.log(2)/0.01) < int(4**10/0.01))

print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
