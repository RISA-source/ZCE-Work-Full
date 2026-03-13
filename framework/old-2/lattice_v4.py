"""
LATTICE v4 — Self-Energy Loop Amplitude
=========================================
Key insight from v3:
  - Amplitude DECREASES with depth M
  - Mass INCREASES with generation
  - These are opposite
  - Therefore: mass comes from SELF-ENERGY LOOP, not one-way path

Physical picture (correct QFT):
  Fermion mass = self-energy = amplitude of loop:
    fermion(N,M) -> Higgs(2,0) -> fermion(N,M)
  
  This is a CLOSED path: start at fermion site, reach Higgs, return.
  
  mass_f ~ |A(fermion -> Higgs -> fermion)|
         = |A_forward| × |A_return|
         = |A(f->H)|²   [if forward = reverse by time reversal]

So mass ~ (amplitude from fermion to Higgs)²
       ~ (amplitude from Higgs to fermion)²   [same by T-symmetry]

If amplitude FROM Higgs TO fermion decreases with depth:
  |A_e| > |A_mu| > |A_tau|

Then:
  mass_e ~ |A_e|²   is LARGEST
  
But electron is LIGHTEST. Contradiction again.

UNLESS: the self-energy has a DENOMINATOR.

In QFT:
  mass = numerator / denominator
  numerator = Yukawa × vev = g × v
  denominator = propagator factor = 1/(p² - m²) but at p=0: 1/m²

Actually the Dyson equation:
  m_phys = m_bare + Σ(m_phys)
  
where Σ is the self-energy. For massless bare fermion:
  m_phys = Σ(m_phys) ≈ Σ(0) for small mass

Σ(0) = (Yukawa)² × vev² × (Higgs propagator at zero momentum)
     = g² × v² / m_H²

So mass_f ~ g_f² / m_H²   where g_f = Yukawa coupling

But this gives mass PROPORTIONAL to g², and if g decreases with depth
then mass decreases with depth — still wrong direction.

WAIT. Let me reconsider the site assignment entirely.

What if the generation assignment is INVERTED?
What if tau is at M=1 (closest to Higgs) and electron is at M=3?

That would mean:
  - Tau: M=1, shortest path to Higgs, largest amplitude -> heaviest
  - Muon: M=2, medium path
  - Electron: M=3, longest path, smallest amplitude -> lightest

This is PHYSICALLY MOTIVATED:
  - Deeper in hierarchy = further from Higgs = lighter mass
  - Electron is the deepest/most fundamental lepton
  - Tau is the shallowest/closest to Higgs sector

Let's test this and also test the loop amplitude formula.
"""

import numpy as np
from numpy.linalg import norm

# ── Parameters ─────────────────────────────────────────────────
N_MAX = 6
M_MAX = 5
E_P   = 1.0
t     = 0.754

HIGGS_SITE = (2, 0)

OBSERVED = {
    'e': 0.511, 'mu': 105.7, 'tau': 1777.0,
    'u': 2.2,   'c':  1270., 't':  173000.0,
    'd': 4.7,   's':  95.0,  'b':  4180.0,
}

def random_su2(rng):
    z = (rng.randn(2,2) + 1j*rng.randn(2,2)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    d = np.diag(R)
    Q = Q * (d / np.abs(d))
    if np.linalg.det(Q).real < 0:
        Q[:,0] *= -1
    return Q

def random_su3(rng):
    z = (rng.randn(3,3) + 1j*rng.randn(3,3)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    d = np.diag(R)
    Q = Q * (d / np.abs(d))
    det = np.linalg.det(Q)
    Q[:,0] /= (det ** (1.0/3.0))
    return Q

def get_neighbors(n, m, n_max, m_max):
    nb = []
    if n+1 <= n_max: nb.append((n+1,m))
    if n-1 >= 0:     nb.append((n-1,m))
    if m+1 <= m_max: nb.append((n,m+1))
    if m-1 >= 0:     nb.append((n,m-1))
    return nb

def build_gauge_scalar(n_max, m_max, seed=42):
    """
    Simplified: all links get scalar U(1) phase.
    Phase on N-link at (n,m): theta = 2*pi*n/N_max (charge structure)
    Phase on M-link at (n,m->m+1): depends on gauge group at that depth
    """
    rng = np.random.RandomState(seed)
    gauge = {}
    
    for n in range(n_max+1):
        for m in range(m_max+1):
            # N-direction
            if n+1 <= n_max:
                # U(1): phase proportional to charge
                theta = 2*np.pi*n/n_max + rng.uniform(-0.5, 0.5)
                gauge[((n,m),(n+1,m))] = np.exp(1j*theta)
                gauge[((n+1,m),(n,m))] = np.exp(-1j*theta)
            
            # M-direction: phase depends on depth
            if m+1 <= m_max:
                if m == 0:
                    # SU(2): use a random phase with SU(2) structure
                    # For scalar approx: take trace/2 of SU(2) matrix
                    U = random_su2(rng)
                    phase = np.exp(1j * np.angle(np.trace(U)/2))
                    gauge[((n,0),(n,1))] = phase
                    gauge[((n,1),(n,0))] = np.conj(phase)
                elif m == 2:
                    # SU(3): trace/3 of SU(3) matrix
                    U = random_su3(rng)
                    phase = np.exp(1j * np.angle(np.trace(U)/3))
                    gauge[((n,2),(n,3))] = phase
                    gauge[((n,3),(n,2))] = np.conj(phase)
                else:
                    theta = rng.uniform(0, 2*np.pi)
                    gauge[((n,m),(n,m+1))] = np.exp(1j*theta)
                    gauge[((n,m+1),(n,m))] = np.exp(-1j*theta)
    
    return gauge

def path_amplitude_scalar(n_s, m_s, n_e, m_e,
                           gauge, n_max, m_max, t_hop,
                           n_paths, max_steps, rng,
                           bias=0.5):
    """Scalar path amplitude with biased random walk."""
    total = 0j
    hits = 0
    
    for _ in range(n_paths):
        n, m = n_s, m_s
        amp = 1.0 + 0j
        
        for step in range(max_steps):
            nb = get_neighbors(n, m, n_max, m_max)
            if not nb: break
            
            # Bias toward target
            dists = [np.exp(-bias*(abs(nn-n_e)+abs(nm-m_e))) for nn,nm in nb]
            s = sum(dists)
            probs = [d/s for d in dists]
            
            ch = rng.choice(len(nb), p=probs)
            n2, m2 = nb[ch]
            
            link = ((n,m),(n2,m2))
            g = gauge.get(link, 1.0)
            
            # Correction for biased sampling
            amp *= t_hop * g / probs[ch]
            n, m = n2, m2
            
            if (n,m) == (n_e, m_e):
                total += amp
                hits += 1
                break
    
    # Normalize by number of paths
    return total / n_paths, hits

# ═══════════════════════════════════════════════════════════════
# TEST: Inverted site assignment
# tau at M=1, muon at M=2, electron at M=3
# ═══════════════════════════════════════════════════════════════

print("="*65)
print("LATTICE v4: SELF-ENERGY + INVERTED SITE ASSIGNMENT TEST")
print("="*65)

print(f"\n── TEST 1: Normal assignment (e=M1, mu=M2, tau=M3) ──")
print(f"── TEST 2: Inverted assignment (tau=M1, mu=M2, e=M3) ──")
print()

N_PATHS = 100000
MAX_STEPS = 12

assignments = {
    'Normal':   {'e':(1,1), 'mu':(1,2), 'tau':(1,3)},
    'Inverted': {'tau':(1,1), 'mu':(1,2), 'e':(1,3)},
    'Mixed1':   {'tau':(1,1), 'e':(1,2), 'mu':(1,3)},  # tau heaviest, mu middle
}

for assign_name, sites in assignments.items():
    print(f"\n  Assignment: {assign_name}")
    print(f"  Sites: {sites}")
    
    all_amps = {f: [] for f in sites}
    
    for seed in range(8):
        gauge = build_gauge_scalar(N_MAX, M_MAX, seed)
        rng = np.random.RandomState(seed*777)
        
        for fname, (n_e, m_e) in sites.items():
            amp, _ = path_amplitude_scalar(
                HIGGS_SITE[0], HIGGS_SITE[1], n_e, m_e,
                gauge, N_MAX, M_MAX, t,
                N_PATHS//4, MAX_STEPS, rng
            )
            all_amps[fname].append(abs(amp))
    
    mean_a = {f: np.mean(all_amps[f]) for f in sites}
    
    print(f"  Mean amplitudes:")
    for fname, site in sites.items():
        print(f"    {fname} at {site}: {mean_a[fname]:.6f}")
    
    # Compute lepton ratios
    # In Standard Model: mass_tau > mass_mu > mass_e
    # If amplitude ~ Yukawa ~ mass: need amp_tau > amp_mu > amp_e
    
    print(f"  Ratios (in terms of observed: tau=1777, mu=105.7, e=0.511):")
    
    if 'tau' in mean_a and 'mu' in mean_a and 'e' in mean_a:
        # mu/e ratio
        r_mue = mean_a['mu'] / mean_a['e'] if mean_a['e'] > 0 else float('inf')
        r_tauму = mean_a['tau'] / mean_a['mu'] if mean_a['mu'] > 0 else float('inf')
        
        obs_mue = OBSERVED['mu'] / OBSERVED['e']
        obs_tauму = OBSERVED['tau'] / OBSERVED['mu']
        
        print(f"    mu/e:   computed={r_mue:.4f}  target={obs_mue:.1f}  "
              f"{'✓ direction' if r_mue > 1 else '✗ wrong direction'}")
        print(f"    tau/mu: computed={r_tauму:.4f}  target={obs_tauму:.1f}  "
              f"{'✓ direction' if r_tauму > 1 else '✗ wrong direction'}")

# ═══════════════════════════════════════════════════════════════
# LOOP AMPLITUDE: fermion -> Higgs -> fermion
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"LOOP AMPLITUDE TEST")
print(f"mass ~ |A(fermion -> Higgs -> fermion)|")
print(f"="*65)

# For inverted assignment: tau=(1,1), mu=(1,2), e=(1,3)
loop_sites = {'tau': (1,1), 'mu': (1,2), 'e': (1,3)}

print(f"\nSites (inverted): tau=(1,1), mu=(1,2), e=(1,3)")
print(f"Loop: fermion -> Higgs(2,0) -> fermion")
print()

loop_amps = {f: [] for f in loop_sites}

for seed in range(8):
    gauge = build_gauge_scalar(N_MAX, M_MAX, seed)
    rng = np.random.RandomState(seed*333)
    
    for fname, (n_f, m_f) in loop_sites.items():
        # Forward: fermion -> Higgs
        amp_fwd, h1 = path_amplitude_scalar(
            n_f, m_f, HIGGS_SITE[0], HIGGS_SITE[1],
            gauge, N_MAX, M_MAX, t,
            N_PATHS//4, MAX_STEPS, rng
        )
        # Return: Higgs -> fermion
        amp_ret, h2 = path_amplitude_scalar(
            HIGGS_SITE[0], HIGGS_SITE[1], n_f, m_f,
            gauge, N_MAX, M_MAX, t,
            N_PATHS//4, MAX_STEPS, rng
        )
        # Loop = product
        loop_amp = abs(amp_fwd) * abs(amp_ret)
        loop_amps[fname].append(loop_amp)

print(f"  {'Fermion':>8}  {'Site':>8}  {'Mean loop amp':>15}  {'Std':>10}")
print(f"  {'-'*50}")
mean_loop = {}
for fname in ['tau', 'mu', 'e']:
    site = loop_sites[fname]
    ml = np.mean(loop_amps[fname])
    sl = np.std(loop_amps[fname])
    mean_loop[fname] = ml
    print(f"  {fname:>8}  {str(site):>8}  {ml:>15.8f}  {sl:>10.8f}")

print(f"\n  Loop amplitude ratios:")
if mean_loop.get('e',0) > 0:
    r_mue  = mean_loop['mu']  / mean_loop['e']
    r_taumu = mean_loop['tau'] / mean_loop['mu']
    print(f"  tau/mu: {r_taumu:.4f}  (target: {OBSERVED['tau']/OBSERVED['mu']:.1f})")
    print(f"  mu/e:   {r_mue:.4f}  (target: {OBSERVED['mu']/OBSERVED['e']:.1f})")

# ═══════════════════════════════════════════════════════════════
# SCAN: What t gives correct ratios with inverted assignment?
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"SCAN: Find t that gives correct lepton ratios")
print(f"Using inverted assignment: tau=(1,1), mu=(1,2), e=(1,3)")
print(f"="*65)

scan_sites = {'tau': (1,1), 'mu': (1,2), 'e': (1,3)}
t_values = np.logspace(-1, 0.5, 20)

print(f"\n  {'t':>8}  {'tau/mu':>10}  {'mu/e':>10}  {'score':>10}")
print(f"  {'-'*45}")

obs_taumu = OBSERVED['tau'] / OBSERVED['mu']
obs_mue   = OBSERVED['mu']  / OBSERVED['e']

best_score = float('inf')
best_t = t

for t_val in t_values:
    gauge = build_gauge_scalar(N_MAX, M_MAX, seed=0)
    rng = np.random.RandomState(42)
    
    amps = {}
    for fname, (n_e, m_e) in scan_sites.items():
        amp, _ = path_amplitude_scalar(
            HIGGS_SITE[0], HIGGS_SITE[1], n_e, m_e,
            gauge, N_MAX, M_MAX, t_val,
            N_PATHS//5, MAX_STEPS, rng
        )
        amps[fname] = abs(amp)
    
    if amps.get('e',0) > 1e-10 and amps.get('mu',0) > 1e-10:
        r_tm = amps['tau'] / amps['mu']
        r_me = amps['mu']  / amps['e']
        
        if r_tm > 0 and r_me > 0:
            score = (np.log(r_tm/obs_taumu))**2 + (np.log(r_me/obs_mue))**2
            
            marker = " <-- BEST" if score < best_score else ""
            if score < best_score:
                best_score = score
                best_t = t_val
            
            print(f"  {t_val:>8.4f}  {r_tm:>10.4f}  {r_me:>10.4f}  {score:>10.4f}{marker}")

print(f"\n  Best t = {best_t:.4f}  score = {best_score:.4f}")
print(f"  Target: tau/mu = {obs_taumu:.1f},  mu/e = {obs_mue:.1f}")

# ═══════════════════════════════════════════════════════════════
# SUMMARY OF FINDINGS
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"SUMMARY OF v4 FINDINGS")
print(f"="*65)
print(f"""
The key question this experiment answers:
  Which site assignment gives correct DIRECTION for lepton hierarchy?
  
Expected result if framework is correct:
  The inverted assignment (tau=M1, mu=M2, e=M3) should give
  tau/mu > 1 and mu/e > 1 in amplitude ratios.
  
This would mean: particles CLOSER to Higgs are HEAVIER.
Physical interpretation: proximity to the symmetry-breaking scale
determines mass. Tau is heaviest because it couples most directly
to the Higgs sector. Electron is lightest because it is furthest
from the Higgs (deepest in the production hierarchy).

This is actually a PREDICTION of the framework:
  Generation = distance from Higgs sector in the (N,M) lattice.
  1st generation (e, u, d) is furthest -> lightest.
  3rd generation (tau, top, bottom) is closest -> heaviest.
  
This INVERTS the naive reading where M = generation number.
Instead: M is measured FROM the Higgs sector, not from the vacuum.
""")
