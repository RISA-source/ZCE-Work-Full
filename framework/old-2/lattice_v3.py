"""
LATTICE HAMILTONIAN v3 — Gauge Field Path Integral
====================================================
Key insight from v2:
  - Mass = path amplitude from Higgs site to fermion site
  - Random phases give WRONG direction (mu < e)
  - Need CORRECT gauge group phases: U(1), SU(2), SU(3)

STRUCTURE:
  - N-direction links carry U(1) phase: e^{i*theta_N}
  - M=1 links carry SU(2) matrix (2x2 unitary)
  - M=3 links carry SU(3) matrix (3x3 unitary)
  - Amplitude = product of matrices along path
  - Mass = |sum over all paths of path amplitudes|

GAUGE FIELD ASSIGNMENT (from token structure):
  N-links (N->N+1 at fixed M): U(1) phase = 2*pi*N/N_max
    Because N encodes electric charge, U(1) acts on N-sector.
  
  M-links at M=0->1: SU(2) matrix (weak force, doublet structure)
    The two contexts at M=1: (N=0,M=1) and (N=1,M=1) form doublet.
    SU(2) mixes them.
  
  M-links at M=2->3: SU(3) matrix (strong force, color triplet)
    The three 1-bits at M=3 form color triplet.
    SU(3) acts on (N=0,M=3), (N=1,M=3), (N=2,M=3).

HIGGS mechanism:
  Higgs site: (N=2, M=0)
  SU(2) breaking: gives mass to W/Z, modifies M=0->1 hopping
  After breaking: one neutral component gets vev v
  Yukawa coupling = amplitude from (N=2,M=0) to fermion site
"""

import numpy as np
from numpy.linalg import norm, eigh
from functools import lru_cache

# ── Parameters ─────────────────────────────────────────────────
N_MAX = 6
M_MAX = 4
E_P   = 1.0
t     = 0.754   # hopping amplitude from v1 best fit
N_PATHS = 200000
MAX_STEPS = 15

HIGGS_SITE = (2, 0)

# Observed masses (MeV)
OBSERVED = {
    'e': 0.511, 'mu': 105.7, 'tau': 1777.0,
    'u': 2.2,   'c':  1270., 't':  173000.0,
    'd': 4.7,   's':  95.0,  'b':  4180.0,
}

# ── SU(2) and SU(3) random matrix generators ───────────────────

def random_su2(rng):
    """Generate random SU(2) matrix using Haar measure"""
    # Parametrize as a + i*b*sigma where a^2+|b|^2=1
    # Use QR decomposition of random complex 2x2
    z = (rng.randn(2,2) + 1j*rng.randn(2,2)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    # Fix phases to make it SU(2) not just U(2)
    d = np.diag(R)
    Q = Q * (d / np.abs(d))
    if np.linalg.det(Q).real < 0:
        Q[:,0] *= -1
    return Q

def random_su3(rng):
    """Generate random SU(3) matrix using Haar measure"""
    z = (rng.randn(3,3) + 1j*rng.randn(3,3)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    d = np.diag(R)
    Q = Q * (d / np.abs(d))
    det = np.linalg.det(Q)
    Q[:,0] /= (det ** (1.0/3.0))
    return Q

def u1_phase(n, n_max):
    """U(1) phase for N-direction hop at position n"""
    return np.exp(2j * np.pi * n / max(n_max, 1))

# ── Build gauge field configuration ────────────────────────────

def build_gauge_fields(n_max, m_max, seed=42):
    """
    Build gauge field on each link of the (N,M) lattice.
    Returns dict: link -> gauge matrix/phase
    
    Link types:
      'N': (n,m) -> (n+1,m)  : U(1) phase (scalar)
      'M01': (n,0) -> (n,1)  : SU(2) 2x2 matrix
      'M12': (n,1) -> (n,2)  : SU(2) 2x2 matrix  
      'M23': (n,2) -> (n,3)  : SU(3) 3x3 matrix
      'M34': (n,3) -> (n,4)  : SU(3) 3x3 matrix (if m_max >= 4)
      'M_other': other M links: U(1) phase
    """
    rng = np.random.RandomState(seed)
    gauge = {}
    
    for n in range(n_max+1):
        for m in range(m_max+1):
            # N-direction link: (n,m) -> (n+1,m)
            if n+1 <= n_max:
                # U(1) phase from charge structure
                # Physical: theta = integral of A_mu along link
                # Token structure: N encodes charge, so phase ~ 2pi*N/N_max
                # But also allow fluctuation (gauge field is not fixed)
                theta = 2*np.pi*n/n_max + rng.uniform(-0.3, 0.3)
                gauge[((n,m),(n+1,m))] = np.exp(1j * theta)
                gauge[((n+1,m),(n,m))] = np.exp(-1j * theta)
            
            # M-direction links
            if m+1 <= m_max:
                if m == 0:
                    # M=0->1: SU(2) weak doublet structure
                    # This is where SU(2) symmetry breaking happens
                    # Before breaking: full SU(2) matrix
                    # After Higgs mechanism: mostly diagonal
                    U = random_su2(rng)
                    # Higgs vev breaks SU(2): tilt toward neutral direction
                    # Mix in identity: U -> cos(alpha)*I + sin(alpha)*U
                    alpha = np.pi/4  # maximal mixing for now
                    U_broken = np.cos(alpha)*np.eye(2,dtype=complex) + np.sin(alpha)*U
                    # Normalize rows
                    for row in range(2):
                        U_broken[row] /= norm(U_broken[row])
                    gauge[((n,0),(n,1))] = U_broken
                    gauge[((n,1),(n,0))] = U_broken.conj().T
                    
                elif m == 1:
                    # M=1->2: intermediate, SU(2) still active
                    U = random_su2(rng)
                    gauge[((n,1),(n,2))] = U
                    gauge[((n,2),(n,1))] = U.conj().T
                    
                elif m == 2:
                    # M=2->3: SU(3) color structure begins
                    U = random_su3(rng)
                    gauge[((n,2),(n,3))] = U
                    gauge[((n,3),(n,2))] = U.conj().T
                    
                elif m == 3:
                    # M=3->4: SU(3) continues
                    U = random_su3(rng)
                    gauge[((n,3),(n,4))] = U
                    gauge[((n,4),(n,3))] = U.conj().T
                    
                else:
                    # Other M links: U(1) phase
                    theta = rng.uniform(0, 2*np.pi)
                    gauge[((n,m),(n,m+1))] = np.exp(1j*theta)
                    gauge[((n,m+1),(n,m))] = np.exp(-1j*theta)
    
    return gauge

def get_link_amplitude(site1, site2, gauge, t_hop):
    """
    Get hopping amplitude from site1 to site2.
    Returns scalar or matrix depending on gauge group.
    """
    link = (site1, site2)
    if link not in gauge:
        return t_hop  # default real hopping
    
    g = gauge[link]
    if np.isscalar(g) or g.shape == ():
        return t_hop * g
    else:
        # Matrix-valued: return t * matrix
        return t_hop * g

# ── Path integral Monte Carlo ───────────────────────────────────

def compute_yukawa_amplitude(n_start, m_start, n_end, m_end,
                              gauge, n_max, m_max, t_hop,
                              n_paths, max_steps, rng):
    """
    Compute Yukawa coupling = sum over paths from (n_start,m_start) to (n_end,m_end).
    
    For scalar paths: amplitude = product of scalar hops
    For matrix paths: amplitude = trace of product of matrices
    
    Uses importance sampling: paths weighted by |amplitude|^2.
    """
    # Determine if we need matrix or scalar amplitudes
    # If path goes through M=0->1 or M=2->3, it picks up SU(2) or SU(3) matrices
    
    total_amplitude = 0j
    total_weight = 0
    paths_hit = 0
    
    for path_i in range(n_paths):
        n, m = n_start, m_start
        amp = 1.0 + 0j
        is_matrix = False
        mat_amp = None
        
        for step in range(max_steps):
            # Get neighbors
            neighbors = []
            if n+1 <= n_max: neighbors.append((n+1, m))
            if n-1 >= 0:     neighbors.append((n-1, m))
            if m+1 <= m_max: neighbors.append((n, m+1))
            if m-1 >= 0:     neighbors.append((n, m-1))
            
            if not neighbors:
                break
            
            # Biased random walk: prefer steps toward target
            # Compute distance to target for each neighbor
            dists = []
            for (nn, nm) in neighbors:
                d = abs(nn - n_end) + abs(nm - m_end)
                dists.append(np.exp(-d * 0.5))  # bias toward target
            
            total_d = sum(dists)
            probs = [d/total_d for d in dists]
            
            choice = rng.choice(len(neighbors), p=probs)
            n2, m2 = neighbors[choice]
            
            # Get link amplitude
            link_amp = get_link_amplitude((n,m), (n2,m2), gauge, t_hop)
            
            # Handle matrix vs scalar
            if hasattr(link_amp, 'shape') and len(link_amp.shape) > 0:
                if mat_amp is None:
                    # Initialize matrix amplitude as identity * scalar amp
                    dim = link_amp.shape[0]
                    mat_amp = amp * link_amp
                else:
                    # Check dimension compatibility - if mismatch, take trace and restart
                    if mat_amp.shape[1] != link_amp.shape[0]:
                        # Dimension mismatch: collapse current matrix to scalar
                        amp = np.trace(mat_amp) / mat_amp.shape[0]
                        mat_amp = amp * link_amp
                    else:
                        mat_amp = mat_amp @ link_amp
                amp = 1.0  # track separately
                is_matrix = True
            else:
                if is_matrix:
                    mat_amp = mat_amp * link_amp
                else:
                    amp *= link_amp
            
            # Correction for biased sampling
            amp_correction = 1.0 / (probs[choice] * len(neighbors))
            if is_matrix:
                mat_amp *= amp_correction
            else:
                amp *= amp_correction
            
            n, m = n2, m2
            
            if (n, m) == (n_end, m_end):
                # Reached target
                if is_matrix and mat_amp is not None:
                    # Take trace / dimension for scalar mass
                    dim = mat_amp.shape[0]
                    contribution = np.trace(mat_amp) / dim
                else:
                    contribution = amp
                
                total_amplitude += contribution
                total_weight += 1
                paths_hit += 1
                break
    
    return total_amplitude, paths_hit

# ── Main computation ────────────────────────────────────────────

print("="*65)
print("LATTICE v3: GAUGE FIELD PATH INTEGRAL")
print("="*65)
print(f"\nGauge structure:")
print(f"  N-links: U(1) phases (electric charge)")
print(f"  M=0->1:  SU(2) matrices (weak force, broken by Higgs)")
print(f"  M=2->3:  SU(3) matrices (strong force, color)")
print(f"  Other:   U(1) phases")
print(f"\nPath integral: {N_PATHS} paths, max {MAX_STEPS} steps")
print(f"Higgs site: {HIGGS_SITE}")

# ── Lepton sector ───────────────────────────────────────────────
print(f"\n── LEPTON SECTOR ──")
print(f"Sites: e=(1,1), mu=(1,2), tau=(1,3)")
print(f"Averaging over 10 gauge configurations (seeds)...")
print()

lepton_sites = {'e': (1,1), 'mu': (1,2), 'tau': (1,3)}
lepton_amps = {f: [] for f in lepton_sites}

for seed in range(10):
    gauge = build_gauge_fields(N_MAX, M_MAX, seed)
    rng = np.random.RandomState(seed * 1000 + 42)
    
    for fname, (n_end, m_end) in lepton_sites.items():
        amp, hits = compute_yukawa_amplitude(
            HIGGS_SITE[0], HIGGS_SITE[1],
            n_end, m_end,
            gauge, N_MAX, M_MAX, t,
            n_paths=N_PATHS//10,
            max_steps=MAX_STEPS,
            rng=rng
        )
        lepton_amps[fname].append(abs(amp))

print(f"  {'Fermion':>8}  {'Mean |amp|':>12}  {'Std':>10}  {'CV':>8}")
print(f"  {'-'*45}")
mean_amps = {}
for fname in ['e', 'mu', 'tau']:
    amps = lepton_amps[fname]
    mean_a = np.mean(amps)
    std_a  = np.std(amps)
    cv     = std_a/mean_a if mean_a > 0 else float('inf')
    mean_amps[fname] = mean_a
    print(f"  {fname:>8}  {mean_a:>12.6f}  {std_a:>10.6f}  {cv:>8.4f}")

print(f"\n  Amplitude ratios vs observed mass ratios:")
if mean_amps['e'] > 0:
    r_mue   = mean_amps['mu']  / mean_amps['e']
    r_tauму = mean_amps['tau'] / mean_amps['mu']
    print(f"  mu/e:   computed={r_mue:.4f}  observed={OBSERVED['mu']/OBSERVED['e']:.1f}  "
          f"factor={OBSERVED['mu']/OBSERVED['e']/r_mue if r_mue > 0 else 'inf':.1f}x off")
    print(f"  tau/mu: computed={r_tauму:.4f}  observed={OBSERVED['tau']/OBSERVED['mu']:.1f}  "
          f"factor={OBSERVED['tau']/OBSERVED['mu']/r_tauму if r_tauму > 0 else 'inf':.1f}x off")

# ── Check direction ─────────────────────────────────────────────
print(f"\n── DIRECTION CHECK ──")
print(f"Is the hierarchy going the RIGHT way? (e > mu > tau in amplitude = e lightest)")
if mean_amps['e'] > 0 and mean_amps['mu'] > 0 and mean_amps['tau'] > 0:
    if mean_amps['e'] > mean_amps['mu'] > mean_amps['tau']:
        print(f"  YES: e > mu > tau  ✓  Hierarchy correct direction")
    elif mean_amps['e'] < mean_amps['mu']:
        print(f"  NO: mu > e  ✗  Hierarchy inverted - need to rethink site assignment")
    else:
        print(f"  PARTIAL: mixed ordering")

# ── Quark sector ────────────────────────────────────────────────
print(f"\n── QUARK SECTOR ──")
print(f"Sites: u=(2,3), c=(2,?), t=(2,?) - generation assignment unclear")
print(f"Testing natural assignment: same N, different M")
print()

# Try different generation assignments for quarks
quark_configs = [
    {'label': 'up-type M=1,2,3', 'sites': {'u':(2,1),'c':(2,2),'t':(2,3)}},
    {'label': 'up-type M=2,3,4', 'sites': {'u':(2,2),'c':(2,3),'t':(2,4)}},
    {'label': 'up-type N=2 M=1,2,3', 'sites': {'u':(2,1),'c':(2,2),'t':(2,3)}},
]

for config in quark_configs:
    print(f"  Config: {config['label']}")
    gauge = build_gauge_fields(N_MAX, M_MAX, seed=0)
    rng = np.random.RandomState(99)
    
    q_amps = {}
    for fname, (n_end, m_end) in config['sites'].items():
        amp, hits = compute_yukawa_amplitude(
            HIGGS_SITE[0], HIGGS_SITE[1],
            n_end, m_end,
            gauge, N_MAX, M_MAX, t,
            n_paths=N_PATHS//5,
            max_steps=MAX_STEPS,
            rng=rng
        )
        q_amps[fname] = abs(amp)
    
    if q_amps.get('u', 0) > 0:
        r_cu = q_amps['c']/q_amps['u']
        r_tc = q_amps['t']/q_amps['c'] if q_amps.get('c',0) > 0 else 0
        print(f"    u={q_amps['u']:.5f}  c={q_amps['c']:.5f}  t={q_amps['t']:.5f}")
        print(f"    c/u={r_cu:.3f} (obs={OBSERVED['c']/OBSERVED['u']:.1f})  "
              f"t/c={r_tc:.3f} (obs={OBSERVED['t']/OBSERVED['c']:.1f})")
    print()

# ── What t value would be needed? ──────────────────────────────
print(f"\n── FINDING: What controls the mass ratios? ──")
print(f"""
The path amplitude from Higgs(2,0) to fermion at depth M goes as:
  |A(Higgs -> M)| ~ t^(path_length) × |gauge_factor|

For a direct path from (2,0) to (1,M):
  - Must traverse M hops in M-direction
  - Each hop multiplies by gauge matrix
  - Path length ~ M + |N_higgs - N_fermion| + M = 2M + 1

So |A| ~ t^(2M+1) × |gauge_factor|

For leptons at M=1,2,3:
  |A_e|   ~ t^3
  |A_mu|  ~ t^5  
  |A_tau| ~ t^7

Ratios:
  mu/e   ~ t^2 × |gauge_factor_ratio|
  tau/mu ~ t^2 × |gauge_factor_ratio|

If t=0.754:
  t^2 = 0.568  ->  ratio ~ 0.57 per generation step
  But observed: mu/e = 206.8  (ratio > 1, not < 1!)

So pure path-length scaling gives DECREASING amplitudes with depth.
That means HEAVIER particles have SMALLER amplitudes.
That's CORRECT if mass = Yukawa × vev and larger amplitude = heavier.

Wait: we need to check the convention.
  mass ~ Yukawa coupling
  Yukawa coupling = amplitude from Higgs to fermion
  Heavier fermion = LARGER Yukawa = LARGER amplitude

But path integral gives SMALLER amplitude for deeper sites.
CONTRADICTION.

RESOLUTION: The amplitude ratio inverts because of PHASES.
When phases are included, destructive interference at the electron site
REDUCES its amplitude much more than at the muon site.
The electron is LIGHT because its path amplitude is heavily cancelled.
""")

print(f"Electron amplitude (M=1): {mean_amps.get('e', 'N/A')}")
print(f"Muon amplitude (M=2):     {mean_amps.get('mu', 'N/A')}")
print(f"Tau amplitude (M=3):      {mean_amps.get('tau', 'N/A')}")
print()
print(f"Current ordering: ", end="")
if mean_amps.get('e',0) > mean_amps.get('mu',0) > mean_amps.get('tau',0):
    print("e > mu > tau  (need to INVERT for correct mass hierarchy)")
    print("=> Lighter particles have LARGER raw amplitude")
    print("=> The cancellation story: deeper sites = more phase cancellation = lighter mass")
    print("=> This is WRONG for the Standard Model (tau is heavier than muon)")
else:
    print(f"e={mean_amps.get('e',0):.4f}  mu={mean_amps.get('mu',0):.4f}  tau={mean_amps.get('tau',0):.4f}")

print(f"""
CRITICAL REALIZATION:
  The amplitude DECREASES with depth M.
  But mass INCREASES with generation (tau > muon > electron).
  
  These are OPPOSITE.
  
  Therefore: either
  (A) The site assignment is wrong — tau should be at LOWER M, not higher
  (B) The amplitude-to-mass mapping is inverted — smaller amplitude = lighter
      (this would mean Yukawa ~ 1/amplitude, not amplitude)
  (C) The path integral needs to go in the OTHER direction — 
      from fermion site TO Higgs, not Higgs TO fermion
  (D) We need BOTH direct and return paths — the fermion mass comes from
      the loop amplitude, not the one-way amplitude
      
Option D is most physically motivated: fermion mass in QFT comes from
the self-energy diagram — a loop from fermion -> Higgs -> fermion.
This is a CLOSED path, not an open path.
""")
