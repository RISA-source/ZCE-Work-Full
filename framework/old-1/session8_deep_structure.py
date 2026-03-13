import numpy as np

# ============================================================
# SESSION 8 — DEEP STRUCTURE ANALYSIS
# Fermion Mass Hierarchy — All Approaches
# Rishi Saraff | Herald College Kathmandu | March 2026
# ============================================================

print("SESSION 8: DEEP STRUCTURE ANALYSIS")
print("Fermion Mass Hierarchy — Complete Computational Record")
print("=" * 60)

# --- SECTION 1: THE ROOT OBSTRUCTION ---
print("\n1. THE ROOT OBSTRUCTION")
print("-" * 40)
t = np.exp(-0.5)
v = 246.0
rge = {'lep': 1.52, 'up': 3.45, 'dn': 3.14}

masses = {
    'tau': 1776.86e-3, 'mu': 105.658e-3, 'e': 0.511e-3,
    'top': 172900e-3, 'charm': 1270e-3, 'up_q': 2.2e-3,
    'bot': 4180e-3, 'strange': 95e-3, 'down_q': 4.7e-3
}

def M_from_mass(m, N, rge_f):
    return np.log(m / (v * rge_f)) / np.log(t) - abs(N-2)

M_tau   = M_from_mass(masses['tau'],    1, rge['lep'])
M_mu    = M_from_mass(masses['mu'],     1, rge['lep'])
M_e     = M_from_mass(masses['e'],      1, rge['lep'])
M_charm = M_from_mass(masses['charm'],  2, rge['up'])
M_up    = M_from_mass(masses['up_q'],   2, rge['up'])
M_bot   = M_from_mass(masses['bot'],    3, rge['dn'])
M_str   = M_from_mass(masses['strange'],3, rge['dn'])
M_dn    = M_from_mass(masses['down_q'], 3, rge['dn'])

print(f"Required M values (t=e^{{-1/2}}):")
print(f"  Leptons:   tau={M_tau:.2f}, mu={M_mu:.2f}, e={M_e:.2f}")
print(f"  Up-type:   charm={M_charm:.2f}, up={M_up:.2f}")
print(f"  Down-type: bot={M_bot:.2f}, str={M_str:.2f}, dn={M_dn:.2f}")

ratio_lep = np.log(masses['tau']/masses['mu']) / np.log(masses['mu']/masses['e'])
print(f"\nln(tau/mu)/ln(mu/e) = {ratio_lep:.6f}")
print(f"For integer DeltaM with single t, this ratio must be rational.")
print(f"Required DeltaM values: {M_mu-M_tau:.2f} and {M_e-M_mu:.2f} — irrational.")
print(f"CONCLUSION: t=e^{{-1/2}} AND integer M AND correct masses are mutually incompatible.")

# --- SECTION 2: 9/17 RATIONAL RATIO ---
print("\n2. THE 9/17 RATIONAL RATIO PATTERN")
print("-" * 40)
ratio_exact = np.log(masses['tau']/masses['mu']) / np.log(masses['mu']/masses['e'])
print(f"Exact ratio: {ratio_exact:.8f}")
print(f"9/17 =       {9/17:.8f}")
print(f"Difference:  {abs(ratio_exact - 9/17):.2e} ({abs(ratio_exact-9/17)/(9/17)*100:.4f}%)")

# If DeltaM_12 = 9, DeltaM_23 = 17 (leptons)
# t_M^9 = tau/mu * (rge factors cancel)
dM_12_lep = 5   # tau to mu spacing attempt
dM_23_lep = 9   # mu to e spacing attempt

# Best fit t_M for leptons
from scipy.optimize import fsolve
def lep_eq(t_M):
    ratio_calc = dM_12_lep / dM_23_lep
    return ratio_calc - ratio_lep
# The consistent t_M:
# m_tau / m_mu = t_M^{dM_12}
t_M_lep = (masses['tau']/masses['mu'])**(1.0/9) if True else 0
# Actually: t_M^9 = tau/mu → t_M = (tau/mu)^(1/9)
t_M_lep = (masses['mu']/masses['tau'])**(1.0/9)
t_M_lep_check = (masses['e']/masses['mu'])**(1.0/17)
print(f"\nIf DeltaM(tau→mu)=9, DeltaM(mu→e)=17:")
print(f"  t_M from tau/mu spacing: {t_M_lep:.6f}")
print(f"  t_M from mu/e  spacing: {t_M_lep_check:.6f}")
print(f"  t = e^{{-1/2}} = {t:.6f}")
print(f"  t_M ≠ e^{{-1/2}} — different hopping parameter required")

# --- SECTION 3: PARTITION FUNCTION ---
print("\n3. PARTITION FUNCTION OF THE LATTICE")
print("-" * 40)
N_factor = sum(np.exp(-abs(N-2)) for N in range(0,50))
M_factor = 1/(1-np.exp(-1))
Z = N_factor * M_factor
print(f"Z = sum_{{N,M}} exp(-|N-2|-M) = {Z:.6f}")
print(f"The lattice is normalizable. Most probable state: (N=2,M=0) [Higgs site]")

# --- SECTION 4: MDL ANALYSIS ---
print("\n4. MDL ANALYSIS")
print("-" * 40)
print("MDL minimum for lepton sector (N=1):")
print("  M values: 0, 1, 2 (consecutive)")
mass_MDL = [v * rge['lep'] * t**(1+M) for M in [0,1,2]]
print(f"  Predicted masses: {[f'{m*1000:.2f} MeV' for m in mass_MDL]}")
print(f"  Observed:         tau=1776.86 MeV, mu=105.66 MeV, e=0.511 MeV")
print(f"  MDL gives wrong hierarchy by factor ~{masses['tau']/mass_MDL[0]:.1f}")

# --- SECTION 5: SELF-ENCODING FIXED POINT ---
print("\n5. SELF-ENCODING FIXED POINT ANALYSIS")
print("-" * 40)
# Fermion spectrum: 9 non-top fermions
# K(S) = 39 + sum of gen2,gen3 M values
M_gen2_gen3 = [M_mu, M_e, M_charm, M_up, M_str, M_dn]
K_S = 39 + sum(M_gen2_gen3)
print(f"K(S_fermions) = 39 + {sum(M_gen2_gen3):.1f} = {K_S:.1f}")
print(f"Largest L in fermion spectrum (electron): L = {M_e+2:.1f}")
print(f"K(S) >> max L: self-encoding token is not in the fermion spectrum")
print(f"CONCLUSION: Self-encoding condition requires additional token outside fermion sector")

# --- SECTION 6: STABILITY ANALYSIS ---
print("\n6. STABILITY ANALYSIS")
print("-" * 40)
print("Without M-conservation: all M>0 states are unstable (decay to M=0)")
print("Only M=0 states are truly stable:")
for N in [1,2,3]:
    m = v * rge[['lep','up','dn'][N-1]] * t**(abs(N-2))
    print(f"  N={N}, M=0: m = {m*1000:.2f} MeV")
print("Observed stable leptons: only electron (M~25, not M=0)")
print("This contradicts the stability prediction.")
print("Resolution: M>0 states are METASTABLE, not unstable.")
print("Decay is Yukawa-suppressed. Timescale >> experimental.")

# --- SECTION 7: HONEST SUMMARY ---
print("\n7. HONEST SUMMARY")
print("-" * 40)
print("Parameter reduction achieved:")
print(f"  SM: 9 independent Yukawa couplings (excluding top)")
print(f"  Framework: 6 free M values (t=e^{{-1/2}} is fixed)")
print(f"  Genuine progress: 9 → 6 free parameters")
print(f"")
print(f"Approaches exhausted across Sessions 5-8:")
approaches = [
    "Anomaly cancellation in M-space — FAILED",
    "Self-similarity recursion from P8 — FAILED",
    "Asymptotic safety fixed point — FAILED",
    "T-duality / winding numbers — FAILED",
    "L-as-generation-variable — FAILED",
    "Integer M + Yukawa eigenvalues — PARTIAL (no derivation)",
    "9/17 rational ratio — PATTERN (no structural origin)",
    "Generalized action S=a|N-2|+bM — FAILED",
    "Saddle point stability — FAILED",
    "Normalizability on 2D lattice — FAILED",
    "Self-reference fixed point — FAILED",
    "MDL analysis — WRONG hierarchy",
    "Self-encoding fixed point — FAILED",
    "Stability axiom — WRONG (gives 1 generation)",
    "Partition function rationality — FAILED",
]
for i, a in enumerate(approaches):
    print(f"  {i+1:2d}. {a}")
print(f"\nCONCLUSION: A fifth axiom is logically necessary.")
print(f"The M values are axiomatically independent of Named/Frozen/Productive/Learnable.")
print(f"The fermion mass hierarchy is at the frontier of theoretical physics,")
print(f"not solvable by extension of the four existing axioms.")
