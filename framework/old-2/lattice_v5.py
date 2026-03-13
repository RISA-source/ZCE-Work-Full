"""
LATTICE v5 — Depth-Dependent Hopping
======================================
Key insight from v4:
  No uniform t satisfies both tau/mu AND mu/e simultaneously.
  -> t must vary by depth level, matching gauge couplings.

From the token structure (document Section 29-33):
  U(1)  coupling: alpha_1 ~ exp(-2) ~ 0.135  -> t_N ~ sqrt(0.135) ~ 0.368
  SU(2) coupling: alpha_2 ~ exp(-3) ~ 0.050  -> t_M01 ~ sqrt(0.050) ~ 0.224
  SU(3) coupling: alpha_3 ~ exp(-2) ~ 0.135  -> t_M23 ~ sqrt(0.135) ~ 0.368

But these are Planck-scale tree-level values.
At low energy (fermion mass scale) they run via RGE.

Measured at M_Z:
  alpha_1(M_Z) = 0.017  -> t_N ~ 0.130
  alpha_2(M_Z) = 0.034  -> t_M01 ~ 0.184  
  alpha_3(M_Z) = 0.118  -> t_M23 ~ 0.344

So M-direction hops at depth M=2->3 (color) should be STRONGER
than M=0->1 (weak). This could explain the hierarchy.

We also try a KEY NEW IDEA:
  What if the N-direction hopping is suppressed by MDL cost difference?
  A token at (N,M) costs N+M+1 bits.
  Moving N->N+1 at fixed M costs 1 extra bit.
  MDL suppression: t_N-hop = t * exp(-delta_cost) = t * exp(-1) ~ 0.37*t
  
  But moving M->M+1 at fixed N also costs 1 bit.
  Same suppression.
  
  UNLESS: the gauge group dimension matters.
  At M=1: SU(2) has dimension 3 -> 3 generators -> multiply by 3?
  At M=3: SU(3) has dimension 8 -> 8 generators -> multiply by 8?

This is the "color factor" in QCD: each color has amplitude enhanced
by the number of generators. Let's try this.

ALSO: Test the "N-direction = charge" vs "M-direction = generation"
by trying N-fixed scans (vary M) and M-fixed scans (vary N).
"""

import numpy as np
from numpy.linalg import norm

OBSERVED = {
    'e': 0.511, 'mu': 105.7, 'tau': 1777.0,
    'u': 2.2,   'c':  1270., 't':  173000.0,
    'd': 4.7,   's':  95.0,  'b':  4180.0,
}

N_MAX = 6
M_MAX = 5
HIGGS = (2, 0)

def get_neighbors(n, m, n_max, m_max):
    nb = []
    if n+1 <= n_max: nb.append((n+1,m,'N+'))
    if n-1 >= 0:     nb.append((n-1,m,'N-'))
    if m+1 <= m_max: nb.append((n,m+1,'M+'))
    if m-1 >= 0:     nb.append((n,m-1,'M-'))
    return nb

def random_su2(rng):
    z = (rng.randn(2,2) + 1j*rng.randn(2,2)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    d = np.diag(R)
    Q = Q * (d/np.abs(d))
    if np.linalg.det(Q).real < 0: Q[:,0] *= -1
    return Q

def random_su3(rng):
    z = (rng.randn(3,3) + 1j*rng.randn(3,3)) / np.sqrt(2)
    Q, R = np.linalg.qr(z)
    d = np.diag(R)
    Q = Q * (d/np.abs(d))
    det = np.linalg.det(Q)
    Q[:,0] /= (det**(1.0/3.0))
    return Q

def build_gauge_and_hoppings(n_max, m_max, t_params, seed=42):
    """
    t_params = {
        'N': base N-direction hopping,
        'M01': M=0->1 hopping (weak),
        'M12': M=1->2 hopping,
        'M23': M=2->3 hopping (color),
        'M34': M=3->4 hopping,
        'other': default
    }
    Returns gauge phases and hopping amplitudes per link.
    """
    rng = np.random.RandomState(seed)
    gauge = {}
    hops  = {}
    
    for n in range(n_max+1):
        for m in range(m_max+1):
            # N-direction
            if n+1 <= n_max:
                theta = 2*np.pi*n/n_max + rng.uniform(-0.3,0.3)
                gauge[((n,m),(n+1,m))] = np.exp(1j*theta)
                gauge[((n+1,m),(n,m))] = np.exp(-1j*theta)
                ht = t_params.get('N', t_params.get('other', 0.3))
                hops[((n,m),(n+1,m))] = ht
                hops[((n+1,m),(n,m))] = ht
            
            # M-direction
            if m+1 <= m_max:
                if m == 0:
                    key = 'M01'
                    # SU(2) phase
                    U = random_su2(rng)
                    ph = np.exp(1j*np.angle(np.trace(U)/2))
                elif m == 1:
                    key = 'M12'
                    ph = np.exp(1j*rng.uniform(0, 2*np.pi))
                elif m == 2:
                    key = 'M23'
                    # SU(3) phase
                    U = random_su3(rng)
                    ph = np.exp(1j*np.angle(np.trace(U)/3))
                elif m == 3:
                    key = 'M34'
                    U = random_su3(rng)
                    ph = np.exp(1j*np.angle(np.trace(U)/3))
                else:
                    key = 'other'
                    ph = np.exp(1j*rng.uniform(0, 2*np.pi))
                
                gauge[((n,m),(n,m+1))] = ph
                gauge[((n,m+1),(n,m))] = np.conj(ph)
                ht = t_params.get(key, t_params.get('other', 0.3))
                hops[((n,m),(n,m+1))] = ht
                hops[((n,m+1),(n,m))] = ht
    
    return gauge, hops

def path_amp(n_s, m_s, n_e, m_e, gauge, hops,
             n_max, m_max, n_paths, max_steps, rng, bias=0.5):
    total = 0j
    hits = 0
    for _ in range(n_paths):
        n, m = n_s, m_s
        amp = 1.0+0j
        for _ in range(max_steps):
            nb = get_neighbors(n, m, n_max, m_max)
            if not nb: break
            dists = [np.exp(-bias*(abs(nn-n_e)+abs(nm-m_e))) 
                     for nn,nm,_ in nb]
            s = sum(dists)
            probs = [d/s for d in dists]
            ch = rng.choice(len(nb), p=probs)
            n2, m2, _ = nb[ch]
            link = ((n,m),(n2,m2))
            g  = gauge.get(link, 1.0)
            ht = hops.get(link, 0.3)
            amp *= ht * g / probs[ch]
            n, m = n2, m2
            if (n,m) == (n_e, m_e):
                total += amp; hits += 1; break
    return total/n_paths, hits

def measure_lepton_ratios(t_params, sites, n_seeds=6, n_paths=60000, seed0=0):
    """Measure amplitude ratios for given t_params and site assignment."""
    all_amps = {f: [] for f in sites}
    for seed in range(n_seeds):
        gauge, hops = build_gauge_and_hoppings(N_MAX, M_MAX, t_params, seed+seed0)
        rng = np.random.RandomState(seed*999+42)
        for fname, (n_e, m_e) in sites.items():
            amp, _ = path_amp(HIGGS[0], HIGGS[1], n_e, m_e,
                              gauge, hops, N_MAX, M_MAX,
                              n_paths//n_seeds, 12, rng)
            all_amps[fname].append(abs(amp))
    return {f: np.mean(v) for f, v in all_amps.items()}

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT A: Depth-dependent hopping from gauge couplings
# ═══════════════════════════════════════════════════════════════

print("="*65)
print("LATTICE v5: DEPTH-DEPENDENT HOPPING")
print("="*65)

# Site assignment: tau at M=1 (heaviest), e at M=3 (lightest)
sites_inv = {'tau': (1,1), 'mu': (1,2), 'e': (1,3)}
obs_taumu = OBSERVED['tau']/OBSERVED['mu']  # 16.8
obs_mue   = OBSERVED['mu']/OBSERVED['e']    # 206.8

print(f"\nTarget: tau/mu={obs_taumu:.1f}, mu/e={obs_mue:.1f}")
print(f"Site assignment: tau=(1,1), mu=(1,2), e=(1,3)")

# From gauge couplings at M_Z
t_configs = [
    ('Uniform t=0.3',
     {'N':0.3, 'M01':0.3, 'M12':0.3, 'M23':0.3, 'M34':0.3}),
    ('From alpha(M_Z)',
     {'N':0.130, 'M01':0.184, 'M12':0.260, 'M23':0.344, 'M34':0.344}),
    ('Strong M23 boost',
     {'N':0.2, 'M01':0.2, 'M12':0.4, 'M23':0.8, 'M34':0.8}),
    ('Color factor × SU(3)dim',
     {'N':0.1, 'M01':0.1, 'M12':0.3, 'M23':0.9, 'M34':0.9}),
    ('Very strong M23',
     {'N':0.05, 'M01':0.05, 'M12':0.2, 'M23':1.5, 'M34':1.5}),
    ('Geometric progression',
     {'N':0.1, 'M01':0.1, 'M12':0.1*4, 'M23':0.1*16, 'M34':0.1*16}),
]

print(f"\n  {'Config':>30}  {'tau/mu':>10}  {'mu/e':>10}  {'score':>10}")
print(f"  {'-'*65}")

best_score = float('inf')
best_config = None

for name, t_params in t_configs:
    amps = measure_lepton_ratios(t_params, sites_inv)
    if amps.get('e',0) > 1e-12 and amps.get('mu',0) > 1e-12 and amps.get('tau',0) > 1e-12:
        r_tm = amps['tau']/amps['mu']
        r_me = amps['mu']/amps['e']
        if r_tm > 0 and r_me > 0:
            score = (np.log(r_tm/obs_taumu))**2 + (np.log(r_me/obs_mue))**2
            marker = " ←" if score < best_score else ""
            if score < best_score:
                best_score = score
                best_config = (name, t_params, r_tm, r_me)
            print(f"  {name:>30}  {r_tm:>10.4f}  {r_me:>10.4f}  {score:>10.4f}{marker}")
        else:
            print(f"  {name:>30}  {'neg':>10}  {'neg':>10}  {'N/A':>10}")
    else:
        print(f"  {name:>30}  {'tiny':>10}  {'tiny':>10}  {'N/A':>10}")

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT B: Grid search over t_M12 and t_M23
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"GRID SEARCH: t_M12 vs t_M23")
print(f"Fixed: t_N=t_M01=0.1")
print(f"="*65)

t_base = 0.1
t_M12_vals = [0.1, 0.3, 0.6, 1.0, 1.5, 2.0]
t_M23_vals = [0.1, 0.5, 1.0, 2.0, 3.0, 4.0]

print(f"\n  tau/mu ratios (target={obs_taumu:.1f}):")
print(f"  {'t_M23':>6}", end="")
for t12 in t_M12_vals:
    print(f"  {t12:>8}", end="")
print()

grid_results = {}
for t23 in t_M23_vals:
    print(f"  {t23:>6.1f}", end="")
    for t12 in t_M12_vals:
        tp = {'N':t_base,'M01':t_base,'M12':t12,'M23':t23,'M34':t23}
        amps = measure_lepton_ratios(tp, sites_inv, n_seeds=3, n_paths=30000)
        if amps.get('mu',0) > 1e-12 and amps.get('tau',0) > 1e-12:
            r_tm = amps['tau']/amps['mu']
            grid_results[(t12,t23)] = amps
            print(f"  {r_tm:>8.2f}", end="")
        else:
            print(f"  {'--':>8}", end="")
    print()

print(f"\n  mu/e ratios (target={obs_mue:.1f}):")
print(f"  {'t_M23':>6}", end="")
for t12 in t_M12_vals:
    print(f"  {t12:>8}", end="")
print()

for t23 in t_M23_vals:
    print(f"  {t23:>6.1f}", end="")
    for t12 in t_M12_vals:
        amps = grid_results.get((t12,t23))
        if amps and amps.get('e',0) > 1e-12 and amps.get('mu',0) > 1e-12:
            r_me = amps['mu']/amps['e']
            print(f"  {r_me:>8.2f}", end="")
        else:
            print(f"  {'--':>8}", end="")
    print()

# ═══════════════════════════════════════════════════════════════
# KEY DIAGNOSIS
# ═══════════════════════════════════════════════════════════════

print(f"\n" + "="*65)
print(f"DIAGNOSIS: Can path integrals on this lattice reproduce")
print(f"the observed lepton mass ratios at ALL?")
print(f"="*65)

# The question is: what is the maximum achievable ratio mu/e
# with any t_params configuration?

max_mue = 0
max_config = None

for t23 in [1.0, 2.0, 3.0, 5.0, 8.0]:
    for t12 in [0.05, 0.1, 0.2, 0.3]:
        for t01 in [0.01, 0.05, 0.1]:
            tp = {'N':0.1,'M01':t01,'M12':t12,'M23':t23,'M34':t23}
            amps = measure_lepton_ratios(tp, sites_inv, n_seeds=3, n_paths=20000)
            if amps.get('e',0)>1e-12 and amps.get('mu',0)>1e-12:
                r_me = amps['mu']/amps['e']
                if r_me > max_mue:
                    max_mue = r_me
                    max_config = (tp, amps)

print(f"\n  Maximum achievable mu/e ratio: {max_mue:.2f}")
print(f"  Target: {obs_mue:.1f}")
if max_config:
    tp, amps = max_config
    r_tm = amps.get('tau',0)/amps.get('mu',1)
    print(f"  At this maximum: tau/mu = {r_tm:.2f} (target {obs_taumu:.1f})")
    print(f"  Config: {tp}")

print(f"""
If the maximum achievable mu/e is much less than 206.8:
  -> The simple nearest-neighbor path integral CANNOT produce
     the observed mass hierarchy with ANY t_params.
  -> We need either:
     (A) A much larger lattice with more path-length difference
     (B) Complex phase cancellation (Monte Carlo with full SU(3))
     (C) A different lattice geometry entirely
     (D) The Hamiltonian eigenstates, not path amplitudes, are the masses

If the maximum IS close to 206.8:
  -> We've found the right parameter range and need to optimize.
""")
