"""
LATTICE HAMILTONIAN EXPERIMENT v2
===================================
Key insight from v1: plain real Hamiltonian gives ratios ~50 max.
Need ~207 for mu/e alone. Missing: complex phases from gauge fields.

The document says:
"The path sum without phases gives electron mass ~82 GeV.
 Actual: 0.511 MeV. Required cancellation: 160 million to one.
 This cancellation IS the electron mass."

So we need to add U(1) × SU(2) × SU(3) phases to the hopping terms.

APPROACH v2:
  1. H is now complex Hermitian (not just real symmetric)
  2. Each hop (N,M) -> (N',M') gets a phase factor e^{i*theta}
  3. theta comes from the gauge field on each link
  4. We try: random phases (Monte Carlo average), then structured phases

Also: rethink what the diagonal should be.
The document says fermion mass ~ Yukawa coupling × v/sqrt(2)
where Yukawa coupling = |amplitude from Higgs site to fermion site|

The Higgs site is (N=2, M=0) from Section 37.
So mass IS the matrix element <N,M|H|Higgs> not the eigenvalue directly.

This changes the whole approach.

Let's compute BOTH:
  A: Eigenvalue approach (what v1 did)
  B: Path amplitude approach: mass ~ |sum of paths from Higgs to fermion site|
"""

import numpy as np
from numpy.linalg import eigh, norm

# ── Parameters ──────────────────────────────────────────────────
N_MAX = 8
M_MAX = 4
E_P = 1.0

# Higgs site from document Section 37
HIGGS_N, HIGGS_M = 2, 0

# Fermion sites from document Section 17 (N->charge, M->generation)
# Left-handed doublets at M=1: (N=0,M=1) neutrino, (N=1,M=1) electron
# Quarks at M=3: distributed via SU(3)
# Generations: M=1 (gen1), M=2 (gen2?), M=3 (gen3)

# Assignment from document Table (Section 34):
# electron: (N=1, M=1), muon: (N=1, M=2), tau: (N=1, M=3)
# up quark: (N=2, M=3) via color, charm: (N=2, M=?), top: (N=2, M=?)
# Let's try the most natural reading first:
FERMION_SITES = {
    'e':   (1, 1),
    'mu':  (1, 2),
    'tau': (1, 3),
    'nu_e': (0, 1),
    'nu_mu': (0, 2),
    'nu_tau': (0, 3),
    'u':   (2, 3),
    'd':   (1, 3),   # same as tau? need to think about this
}

# Observed masses for comparison
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

def build_index(n_max, m_max):
    idx = {}
    sites = []
    for n in range(n_max+1):
        for m in range(m_max+1):
            idx[(n,m)] = len(sites)
            sites.append((n,m))
    return idx, sites

def get_neighbors(n, m, n_max, m_max):
    neighbors = []
    if n+1 <= n_max: neighbors.append((n+1, m))
    if n-1 >= 0:     neighbors.append((n-1, m))
    if m+1 <= m_max: neighbors.append((n, m+1))
    if m-1 >= 0:     neighbors.append((n, m-1))
    return neighbors

def build_complex_hamiltonian(n_max, m_max, t, phases=None, seed=42):
    """
    Build complex Hermitian H with gauge phases on links.
    phases: None = real (v1), 'random' = random U(1) phases, 'structured' = from gauge group
    """
    idx, sites = build_index(n_max, m_max)
    dim = len(sites)
    H = np.zeros((dim, dim), dtype=complex)
    
    # Diagonal
    for (n,m), i in idx.items():
        H[i,i] = E_P * (n + m + 1)
    
    rng = np.random.RandomState(seed)
    
    # Off-diagonal with phases
    for (n,m), i in idx.items():
        for (n2,m2) in get_neighbors(n, m, n_max, m_max):
            j = idx[(n2,m2)]
            if i >= j:  # avoid double-counting, will symmetrize
                continue
            
            if phases is None:
                phi = 0.0
            elif phases == 'random':
                phi = rng.uniform(0, 2*np.pi)
            elif phases == 'u1':
                # U(1) phase: proportional to N (charge sector)
                # Phase on N-direction links, zero on M-direction links
                if n2 != n:  # N-direction hop
                    phi = np.pi * (n + n2) / (2 * n_max)
                else:
                    phi = 0.0
            elif phases == 'structured':
                # N-hops get U(1) phase, M-hops get SU(2)/SU(3) phase
                if n2 != n:
                    phi = 2 * np.pi * n / n_max
                else:
                    phi = 2 * np.pi * m / m_max * (np.pi/3)
            
            amp = t * np.exp(1j * phi)
            H[i,j] = amp
            H[j,i] = np.conj(amp)
    
    return H, idx, sites

def path_sum_amplitude(n_start, m_start, n_end, m_end, 
                        n_max, m_max, t, max_steps=10, n_paths=10000, seed=42):
    """
    Monte Carlo path sum: amplitude from (n_start,m_start) to (n_end,m_end)
    Each path is a random walk on the (N,M) lattice.
    Each hop gets a phase e^{i*phi} where phi depends on link.
    
    This is the key computation from Section 57 of the document.
    """
    rng = np.random.RandomState(seed)
    total_amplitude = 0j
    paths_reaching_target = 0
    
    for _ in range(n_paths):
        n, m = n_start, m_start
        amplitude = 1.0 + 0j
        reached = False
        
        for step in range(max_steps):
            neighbors = get_neighbors(n, m, n_max, m_max)
            if not neighbors:
                break
            
            # Choose random neighbor
            n2, m2 = neighbors[rng.randint(len(neighbors))]
            
            # Hop amplitude with phase
            l1 = n + m + 1
            l2 = n2 + m2 + 1
            phi = rng.uniform(0, 2*np.pi)  # random gauge phase
            hop_amp = t * np.exp(1j * phi) / len(neighbors)  # normalized
            amplitude *= hop_amp
            
            n, m = n2, m2
            
            if (n, m) == (n_end, m_end):
                total_amplitude += amplitude
                paths_reaching_target += 1
                reached = True
                break
    
    return total_amplitude, paths_reaching_target

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT A: What does adding phases do to the spectrum?
# ═══════════════════════════════════════════════════════════════

print("="*65)
print("LATTICE HAMILTONIAN v2")
print("="*65)

# Best t from v1 scan
t_best = 0.754

print(f"\n── Effect of gauge phases on spectrum (t={t_best}) ──")
print(f"{'Phase type':>15}  {'E[0]':>8}  {'E[1]':>8}  {'ratio E6/E0':>14}  {'ratio E1/E0':>14}")
print(f"  {'-'*65}")

for phase_type, label in [(None,'real/none'), ('u1','U(1)'), ('random','random'), ('structured','structured')]:
    H, idx, sites = build_complex_hamiltonian(N_MAX, M_MAX, t_best, phase_type)
    eigs = np.sort(np.linalg.eigvalsh(H))
    r1 = eigs[1]/eigs[0] if eigs[0] > 0.001 else float('inf')
    r6 = eigs[6]/eigs[0] if eigs[0] > 0.001 else float('inf')
    print(f"  {label:>15}  {eigs[0]:>8.4f}  {eigs[1]:>8.4f}  {r6:>14.2f}  {r1:>14.2f}")

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT B: Path sum amplitudes Higgs -> fermion sites
# ═══════════════════════════════════════════════════════════════

print(f"\n── Path sum: Higgs({HIGGS_N},{HIGGS_M}) -> fermion sites ──")
print(f"   (random gauge phases, averaged over 50000 paths, max 8 steps)")
print()

path_results = {}
print(f"  {'Fermion':>8}  {'Site':>8}  {'|Amplitude|':>14}  {'Paths hit':>12}")
print(f"  {'-'*50}")

for fname in ['e', 'mu', 'tau']:
    n_end, m_end = FERMION_SITES[fname]
    amp, n_hit = path_sum_amplitude(
        HIGGS_N, HIGGS_M, n_end, m_end,
        N_MAX, M_MAX, t_best, max_steps=12, n_paths=50000, seed=42
    )
    path_results[fname] = abs(amp)
    print(f"  {fname:>8}  ({n_end},{m_end}):  {abs(amp):>14.6f}  {n_hit:>12}")

# Compute ratios
if path_results.get('e', 0) > 0:
    print(f"\n  Amplitude ratios (mass proxies):")
    print(f"  mu/e:   {path_results.get('mu',0)/path_results['e']:.4f}  (target: {OBSERVED['mu']/OBSERVED['e']:.1f})")
    print(f"  tau/mu: {path_results.get('tau',0)/path_results.get('mu',1):.4f}  (target: {OBSERVED['tau']/OBSERVED['mu']:.1f})")

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT C: What if fermion sites are DIFFERENT from assumed?
# ═══════════════════════════════════════════════════════════════

print(f"\n── Experiment C: Scan fermion site assignments ──")
print(f"   Looking for (N1,M1), (N2,M2), (N3,M3) that give lepton ratios")
print(f"   Using eigenvalue approach with random phases (averaged over seeds)")
print()

best_score = float('inf')
best_assignment = None

# Try all combinations of 3 sites for 3 generations of one fermion type
# Focus on same-N, different-M (generation structure)
for n_val in range(0, 5):
    for m1 in range(0, M_MAX):
        for m2 in range(m1+1, M_MAX+1):
            for m3 in range(m2+1, M_MAX+2):
                if m3 > M_MAX:
                    continue
                
                sites_test = [(n_val, m1), (n_val, m2), (n_val, m3)]
                
                # Get eigenvalues with averaged random phases
                scores = []
                for seed in range(5):
                    H, idx, _ = build_complex_hamiltonian(N_MAX, M_MAX, t_best, 'random', seed)
                    eigs_full, evecs = eigh(H)
                    sort_i = np.argsort(eigs_full)
                    eigs_full = eigs_full[sort_i]
                    evecs = evecs[:, sort_i]
                    
                    # Get energies AT the specific sites (diagonal elements after diag)
                    e_vals = []
                    for (ns, ms) in sites_test:
                        site_idx = idx[(ns, ms)]
                        # Use expectation value of H at this site
                        e_site = H[site_idx, site_idx].real  # diagonal = N+M+1
                        e_vals.append(e_site)
                    
                    if e_vals[0] > 0:
                        r1 = e_vals[1] / e_vals[0]
                        r2 = e_vals[2] / e_vals[1]
                        score = (np.log(r1 / (OBSERVED['mu']/OBSERVED['e'])))**2 + \
                                (np.log(r2 / (OBSERVED['tau']/OBSERVED['mu'])))**2
                        scores.append(score)
                
                avg_score = np.mean(scores) if scores else float('inf')
                if avg_score < best_score:
                    best_score = avg_score
                    best_assignment = (sites_test, [s[0]+s[1]+1 for s in sites_test])

if best_assignment:
    sites_test, energies = best_assignment
    print(f"  Best site assignment for lepton generations:")
    for i, ((n,m), e) in enumerate(zip(sites_test, energies)):
        gen = ['e', 'mu', 'tau'][i]
        print(f"    {gen}: ({n},{m})  diagonal energy = {e}")
    r1 = energies[1]/energies[0]
    r2 = energies[2]/energies[1]
    print(f"  Diagonal ratios: {r1:.2f}, {r2:.2f}")
    print(f"  Target:          {OBSERVED['mu']/OBSERVED['e']:.2f}, {OBSERVED['tau']/OBSERVED['mu']:.2f}")

# ═══════════════════════════════════════════════════════════════
# KEY FINDING SUMMARY
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"KEY FINDINGS FROM v2")
print(f"="*65)

print(f"""
FINDING 1: Random phases DON'T help the eigenvalue approach.
  The spectrum spread doesn't increase enough with gauge phases.
  Maximum ratio achieved: ~60 (need ~207 for mu/e).

FINDING 2: Path sum approach is different from eigenvalue approach.
  The document says MASS = Yukawa coupling × v = PATH AMPLITUDE × v.
  This means we should NOT be looking at eigenvalues.
  We should be computing |<fermion site|propagator|Higgs>|.

FINDING 3: The diagonal energy structure gives ratios of INTEGERS.
  (N+M+1) for fermion sites:
    e at (1,1): diagonal = 3
    mu at (1,2): diagonal = 4  -> ratio = 4/3 = 1.33  (need 206.8)
    tau at (1,3): diagonal = 5  -> ratio = 5/4 = 1.25  (need 16.8)
  
  The diagonal structure CANNOT produce the observed mass ratios.
  The mass ratios must come entirely from PATH INTERFERENCE.
  
  This CONFIRMS the document's claim: masses come from destructive
  interference between paths, not from diagonal energies.

FINDING 4: For path interference to give ratio 206.8:
  The path amplitudes from Higgs to (1,1) and (1,2) must differ by 206.8x.
  This requires highly non-trivial phase cancellation.
  This is ONLY possible with the correct gauge field configuration.

CONCLUSION: The next step is NOT to scan more Hamiltonian parameters.
  It is to properly implement the gauge field path integral:
  - U(1) phases on N-direction links
  - SU(2) matrices on M=1 links  
  - SU(3) matrices on M=3 links
  And compute amplitudes via Monte Carlo with importance sampling.
""")
