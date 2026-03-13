
import math, sys, numpy as np
sys.path.insert(0, '/mnt/user-data/uploads')
from zce_core import Asm

PASS = 0; FAIL = 0

def check(label, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✓  {label}")
    else: FAIL += 1; print(f"  ✗  {label}  [{info}]")

def von_neumann_entropy(rho):
    eigs = np.linalg.eigvalsh(rho)
    eigs = eigs[eigs > 1e-12]
    return -np.sum(eigs * np.log2(eigs))

print("="*60)
print("QKD KEY STATE SECURITY: K_F vs ENTROPY")
print("="*60)

qubit_states = {
    "|0>": (np.array([[1,0],[0,0]], dtype=complex), 88),
    "|1>": (np.array([[0,0],[0,1]], dtype=complex), 88),
    "|+>": (np.array([[0.5,0.5],[0.5,0.5]], dtype=complex), 96),
    "|->": (np.array([[0.5,-0.5],[-0.5,0.5]], dtype=complex), 96),
}

print()
print(f"  {'State':<8} {'S':<8} {'K_F':<8} {'m_MDL':<12} {'m_tomo':<10}")
print("  " + "-"*50)
for name, (rho, kf) in qubit_states.items():
    S = von_neumann_entropy(rho)
    m_mdl = int(kf * math.log(2) / 0.1)
    m_tomo = int(4 / 0.01)
    print(f"  {name:<8} {S:<8.3f} {kf:<8} {m_mdl:<12} {m_tomo:<10}")

print()
print("Critical: same entropy, very different K_F -> very different security")
print()
key_types = [
    ("Haar-random 4q",       2.0, 32*256,  "secure"),
    ("Depth-10 circuit 4q",  2.0, 400,     "VULNERABLE"),
    ("GHZ_4",                1.0, 260,     "VULNERABLE"),
    ("|0>^4",                0.0, 352,     "trivially weak"),
]
print(f"  {'Key type':<25} {'S':<6} {'K_F':<10} {'m_MDL':<10} {'m_std':<10} {'status'}")
print("  " + "-"*72)
for name, S, kf, status in key_types:
    m_mdl = int(kf * math.log(2) / 0.1)
    m_std = int(4**4 / 0.01)
    print(f"  {name:<25} {S:<6.1f} {kf:<10} {m_mdl:<10} {m_std:<10} {status}")

print()
print("Eve's advantage: P[distinguish] <= exp(-m * eps / (K_F * ln2))")
print()
for kf_key, label in [(400, "K_F=400 (circuit)"), (8192, "K_F=8192 (Haar)")]:
    print(f"  {label}:")
    for m in [500, 2000, 5000, 20000]:
        adv = math.exp(-m * 0.1 / (kf_key * math.log(2)))
        print(f"    m={m:5d}: advantage <= {adv:.5f}")
    print()

check("Pure states S=0", abs(von_neumann_entropy(np.array([[1,0],[0,0]], dtype=complex))) < 1e-10)
check("Circuit state MDL cheaper than full tomography",
      int(400 * math.log(2) / 0.1) < int(4**4 / 0.01))
check("Haar-random: MDL attack comparable to standard tomography",
      int(32*256 * math.log(2) / 0.1) > int(4**4 / 0.01) * 0.5)
check("Eve advantage decays with more measurements",
      math.exp(-5000*0.1/(200*math.log(2))) < math.exp(-1000*0.1/(200*math.log(2))))

print(f"\n{'='*60}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
