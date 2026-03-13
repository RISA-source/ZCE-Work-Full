"""
LATTICE HAMILTONIAN EXPERIMENT
================================
Token system: H = H_diag + H_off
H_diag[N,M] = E_P * (N+M+1)   [set E_P=1 for now, rescale later]
H_off: nearest neighbor hops on (N,M) lattice with amplitude t

We try THREE forms of H_off matrix elements:
  A: constant t
  B: t / (N+M+1)          [power law decay]
  C: t * exp(-|l'-l|/2)   [exponential decay, original document guess]

For nearest neighbors |l'-l| = 1 always, so C reduces to t*exp(-0.5) ≈ 0.607t
So A and C differ only by a constant rescaling of t — effectively the same.
B is genuinely different.

We compare eigenvalue RATIOS to observed fermion mass ratios.

Observed (rough, in MeV):
  Leptons:  e=0.511,  mu=105.7,   tau=1777
  Up-type:  u=2.2,    c=1270,     t=173000
  Down-type: d=4.7,   s=95,       b=4180

Key ratios to match:
  mu/e   ~ 206.8
  tau/mu ~ 16.8
  c/u    ~ 577
  t/c    ~ 136
  s/d    ~ 20.2
  b/s    ~ 44
"""

import numpy as np
from itertools import product

# ── Lattice parameters ───────────────────────────────────────────
N_MAX = 8    # max identity zeros
M_MAX = 4    # max depth ones (M=0..3 for gauge structure, +1 buffer)
E_P   = 1.0  # energy quantum (set to 1, rescale later)

# Observed fermion masses (MeV) for comparison
OBSERVED = {
    'e':   0.511,
    'mu':  105.7,
    'tau': 1777.0,
    'u':   2.2,
    'c':   1270.0,
    't':   173000.0,
    'd':   4.7,
    's':   95.0,
    'b':   4180.0,
}

OBSERVED_RATIOS = {
    'mu/e':   OBSERVED['mu']   / OBSERVED['e'],
    'tau/mu': OBSERVED['tau']  / OBSERVED['mu'],
    'c/u':    OBSERVED['c']    / OBSERVED['u'],
    't/c':    OBSERVED['t']    / OBSERVED['c'],
    's/d':    OBSERVED['s']    / OBSERVED['d'],
    'b/s':    OBSERVED['b']    / OBSERVED['s'],
}

def build_index(n_max, m_max):
    """Build (N,M) -> index and index -> (N,M) maps"""
    idx = {}
    sites = []
    for n in range(n_max+1):
        for m in range(m_max+1):
            idx[(n,m)] = len(sites)
            sites.append((n,m))
    return idx, sites

def build_hamiltonian(n_max, m_max, t, hop_type='constant'):
    """
    Build H matrix on (N,M) lattice.
    hop_type: 'constant', 'power', 'exponential'
    """
    idx, sites = build_index(n_max, m_max)
    dim = len(sites)
    H = np.zeros((dim, dim))
    
    # Diagonal: E_P * (N+M+1)
    for (n,m), i in idx.items():
        H[i,i] = E_P * (n + m + 1)
    
    # Off-diagonal: nearest neighbor hops
    for (n,m), i in idx.items():
        l_nm = n + m + 1
        neighbors = []
        if n+1 <= n_max: neighbors.append((n+1, m))
        if n-1 >= 0:     neighbors.append((n-1, m))
        if m+1 <= m_max: neighbors.append((n, m+1))
        if m-1 >= 0:     neighbors.append((n, m-1))
        
        for (n2,m2) in neighbors:
            j = idx[(n2,m2)]
            l_n2m2 = n2 + m2 + 1
            
            if hop_type == 'constant':
                amp = t
            elif hop_type == 'power':
                amp = t / np.sqrt(l_nm * l_n2m2)   # geometric mean of costs
            elif hop_type == 'exponential':
                amp = t * np.exp(-abs(l_nm - l_n2m2) / 2.0)
                # Note: for nearest neighbors |l'-l|=1 always
                # so this is t * exp(-0.5) = 0.607t (same as constant up to rescaling)
            
            H[i,j] = amp
    
    return H, idx, sites

def get_spectrum(H):
    """Diagonalize H, return sorted eigenvalues"""
    eigenvalues = np.linalg.eigvalsh(H)
    return np.sort(eigenvalues)

def print_spectrum(eigenvalues, n_show=20):
    """Print first n eigenvalues"""
    print(f"  First {min(n_show, len(eigenvalues))} eigenvalues:")
    for i, e in enumerate(eigenvalues[:n_show]):
        print(f"    E[{i:2d}] = {e:.6f}")

def score_against_observed(eigenvalues):
    """
    Try to match eigenvalue ratios to observed fermion mass ratios.
    Returns best score (lower = better).
    """
    # We have 9 charged fermions, 3 generations of 3 types
    # Try taking eigenvalues in groups of 3 and checking ratios
    
    n = len(eigenvalues)
    best_score = float('inf')
    best_match = None
    
    # Strategy: pick 3 eigenvalues as lepton proxies and check ratios
    # Use positive eigenvalues only
    pos_eigs = eigenvalues[eigenvalues > 0]
    
    if len(pos_eigs) < 9:
        return float('inf'), None
    
    # Try all combinations of 3 eigenvalues for leptons
    # Focus on ratio matching, not absolute values
    obs_r1 = OBSERVED_RATIOS['mu/e']   # 206.8
    obs_r2 = OBSERVED_RATIOS['tau/mu'] # 16.8
    
    for i in range(len(pos_eigs)-2):
        for j in range(i+1, len(pos_eigs)-1):
            for k in range(j+1, len(pos_eigs)):
                r1 = pos_eigs[j] / pos_eigs[i]
                r2 = pos_eigs[k] / pos_eigs[j]
                
                # Log-space distance from target ratios
                score = (np.log(r1/obs_r1))**2 + (np.log(r2/obs_r2))**2
                
                if score < best_score:
                    best_score = score
                    best_match = (i, j, k, pos_eigs[i], pos_eigs[j], pos_eigs[k])
    
    return best_score, best_match

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT 1: Basic spectrum for t = E_P * 0.084 (our prediction)
# ═══════════════════════════════════════════════════════════════

print("="*65)
print("LATTICE HAMILTONIAN EXPERIMENT 1")
print("Token system: H_diag = N+M+1, H_off = nearest neighbor")
print("="*65)

t_pred = E_P * (825 / 9803)   # our predicted ratio
print(f"\nPredicted t/E_P = c_Σ/c_interp = 825/9803 = {t_pred:.5f}")

print(f"\nLattice: N ∈ [0,{N_MAX}], M ∈ [0,{M_MAX}]")
print(f"Dimension: {(N_MAX+1)*(M_MAX+1)} sites")

H_const, idx, sites = build_hamiltonian(N_MAX, M_MAX, t_pred, 'constant')
eigs_const = get_spectrum(H_const)

print(f"\n── Constant hopping, t = {t_pred:.5f} ──")
print_spectrum(eigs_const, 15)

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT 2: Scan t values, find which t gives best mass ratios
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("EXPERIMENT 2: Scan t/E_P, find best lepton ratio match")
print("="*65)
print(f"\nTarget: mu/e = {OBSERVED_RATIOS['mu/e']:.1f}, tau/mu = {OBSERVED_RATIOS['tau/mu']:.1f}")

t_values = np.logspace(-3, 0, 50)  # t from 0.001 to 1.0
results = []

for t_val in t_values:
    H, _, _ = build_hamiltonian(N_MAX, M_MAX, t_val, 'constant')
    eigs = get_spectrum(H)
    score, match = score_against_observed(eigs)
    results.append((t_val, score, match))

results.sort(key=lambda x: x[1])
print(f"\nTop 10 t values by lepton ratio score:")
print(f"  {'t/E_P':>10}  {'score':>12}  {'E[i]':>10}  {'E[j]':>10}  {'E[k]':>10}  {'r1':>8}  {'r2':>8}")
print(f"  {'-'*80}")
for t_val, score, match in results[:10]:
    if match:
        i,j,k,ei,ej,ek = match
        r1 = ej/ei; r2 = ek/ej
        print(f"  {t_val:>10.5f}  {score:>12.4f}  {ei:>10.4f}  {ej:>10.4f}  {ek:>10.4f}  {r1:>8.2f}  {r2:>8.2f}")

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT 3: Compare hopping types at best t
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("EXPERIMENT 3: Compare hopping types")
print("="*65)

best_t = results[0][0]
print(f"\nUsing best t = {best_t:.5f}")

for hop_type in ['constant', 'power']:
    H, _, _ = build_hamiltonian(N_MAX, M_MAX, best_t, hop_type)
    eigs = get_spectrum(H)
    score, match = score_against_observed(eigs)
    print(f"\n  {hop_type} hopping, score={score:.4f}")
    if match:
        i,j,k,ei,ej,ek = match
        r1=ej/ei; r2=ek/ej
        print(f"    Best lepton triple: [{i},{j},{k}]")
        print(f"    E = {ei:.4f}, {ej:.4f}, {ek:.4f}")
        print(f"    Ratios: {r1:.2f}, {r2:.2f}")
        print(f"    Target: {OBSERVED_RATIOS['mu/e']:.2f}, {OBSERVED_RATIOS['tau/mu']:.2f}")

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT 4: Larger lattice, check if more structure emerges
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("EXPERIMENT 4: Larger lattice N_MAX=12, M_MAX=6")
print("="*65)

H_big, idx_big, sites_big = build_hamiltonian(12, 6, best_t, 'constant')
eigs_big = get_spectrum(H_big)
score_big, match_big = score_against_observed(eigs_big)

print(f"\nDimension: {len(sites_big)} sites")
print(f"Score: {score_big:.4f}")
if match_big:
    i,j,k,ei,ej,ek = match_big
    r1=ej/ei; r2=ek/ej
    print(f"Best triple: E = {ei:.4f}, {ej:.4f}, {ek:.4f}")
    print(f"Ratios: r1={r1:.2f} (target {OBSERVED_RATIOS['mu/e']:.2f}), r2={r2:.2f} (target {OBSERVED_RATIOS['tau/mu']:.2f})")
    print(f"\nFirst 20 eigenvalues (large lattice):")
    print_spectrum(eigs_big, 20)

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT 5: Look at eigenvectors - where are states localized?
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*65)
print("EXPERIMENT 5: Eigenvector localization")
print("Where are the low-lying states localized on the (N,M) lattice?")
print("="*65)

H_med, idx_med, sites_med = build_hamiltonian(8, 4, best_t, 'constant')
eigenvalues_med, eigenvectors_med = np.linalg.eigh(H_med)
sort_idx = np.argsort(eigenvalues_med)
eigenvalues_med = eigenvalues_med[sort_idx]
eigenvectors_med = eigenvectors_med[:, sort_idx]

print(f"\nTop 12 eigenstates — showing dominant (N,M) components:")
print(f"  {'State':>6}  {'Energy':>8}  {'Top component (N,M)':>20}  {'weight':>8}  {'2nd (N,M)':>12}  {'weight':>8}")
print(f"  {'-'*75}")

for state_i in range(min(12, len(eigenvalues_med))):
    evec = eigenvectors_med[:, state_i]
    weights = evec**2
    sorted_sites_by_weight = np.argsort(weights)[::-1]
    
    top1_idx = sorted_sites_by_weight[0]
    top2_idx = sorted_sites_by_weight[1]
    
    n1,m1 = sites_med[top1_idx]
    n2,m2 = sites_med[top2_idx]
    w1 = weights[top1_idx]
    w2 = weights[top2_idx]
    
    print(f"  {state_i:>6}  {eigenvalues_med[state_i]:>8.4f}  ({n1},{m1}){' ':>14}  {w1:>8.4f}  ({n2},{m2}){' ':>8}  {w2:>8.4f}")

print("\n" + "="*65)
print("SUMMARY")
print("="*65)
print(f"\nPredicted t/E_P from c_Σ/c_interp: {t_pred:.5f}")
print(f"Best fit t/E_P from spectrum scan:  {best_t:.5f}")
ratio_match = abs(np.log(t_pred/best_t))
print(f"Log-space distance: {ratio_match:.3f} ({'GOOD' if ratio_match < 1 else 'POOR'} match)")

print(f"\nObserved fermion mass ratios:")
for k,v in OBSERVED_RATIOS.items():
    print(f"  {k}: {v:.1f}")

print(f"\nNext steps:")
print(f"  1. The spectrum gives us which (N,M) sites correspond to which particles")
print(f"  2. We need to identify which eigenstate = which fermion")
print(f"  3. Then derive the absolute mass scale from E_P")
print(f"  4. Complex phases from gauge fields will be added in next iteration")
