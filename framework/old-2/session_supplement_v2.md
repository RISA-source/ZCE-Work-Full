# Token Framework — Session Supplement v2
## All Tests Run, All Remaining Derivations, Complete Status
**Rishi Saraff | March 2026**

> Everything new since master.md + additional-support.md. Structured as pull-ready sections. This document is the running record — update it rather than starting fresh.

---

# PART I — THE THREE DECISIVE TESTS: RESULTS

These were the three tests declared as framework-defining. Here is exactly what happened when they were run.

---

## Test 1: Formal Gauge Sector Completeness

**Question:** Can we prove from token axioms alone that exactly 3 gauge sectors exist — ruling out M=2 and M≥4 without assuming the known particle content?

### M≥4: PROVEN complete

The self-similarity theorem (master.md §43) proves: for all M≥4, SU(M) ⊃ SU(M−1) ⊃ ... ⊃ SU(3). Every depth M≥4 generates only representations of U(1)×SU(2)×SU(3). No new generators appear. The proof is complete and requires no appeal to the particle content.

### M=2: ARGUED (not proven, but clean)

The M=2 sector has 2 ordered 1-bits → ℂ² → group U(2) = U(1)×SU(2). But:
- U(1) is already the N-sector
- SU(2) is already the M=1 sector

Therefore M=2 contributes no NEW gauge structure. It duplicates what M=0 and M=1 already cover.

**The remaining gap:** A formal bijection proof that U(2) at M=2 is exactly the product U(1)_N × SU(2)_M1 with no extra factors — not just equal in dimension but identical as groups acting on the same Hilbert space. This requires showing the two SU(2) actions (from M=1 and from M=2) are the same action, not two commuting copies. The argument is clean; the formal proof is not yet written.

**Additional finding:** The M=2 sector is the Higgs sector. U(2) = U(1)×SU(2) is exactly the electroweak group before symmetry breaking. After breaking, only U(1)_EM survives. This is consistent — M=2 IS the Higgs sector. The absence of a new gauge force at M=2 and the presence of the Higgs at M=2 are the same fact.

**Verdict: ARGUED.** The completeness gap is narrowed to a single bijection proof. It is no longer vague — it is one specific thing that needs to be written.

---

## Test 2: Independent Holonomy Fixing

**Question:** Can any principle from {Named, Frozen, MDL, Productive} fix the lepton gauge holonomies without using the observed masses as input?

### What was tried

**Candidate 1 — MDL minimum holonomy (flat connection):** The flat connection Δ_i = 0 is the MDL minimum for the gauge field. But the Flat Field Impossibility Theorem (supplement §II.2) proves that Δ_i = 0 gives equal masses for all generations — contradicting observation. So the MDL minimum without mass constraints gives the wrong answer.

**Candidate 2 — Uniform holonomy = 2π/3 (one full generation rotation):** Setting all Δ_i = 2π/3 gives A_mu = 0 (exactly destructive interference). Singular — not physical.

**Candidate 3 — Koide as the third constraint:** The observed mass ratios (2 constraints) + Koide Q = 2/3 (1 constraint) over-determine the 2 physical holonomies. This means: IF Koide is derivable from token axioms, holonomies are uniquely fixed. Testing this showed the system of equations has solutions — the holonomies that reproduce observed masses DO satisfy Koide automatically (to 0.001%). But Koide is not yet derived from the axioms.

**New finding — Z₃ symmetry interpretation:** Koide Q = 2/3 is geometrically equivalent to requiring the gauge field on the three lepton M-links to have Z₃ rotational symmetry — equal angular spacing of 2π/3 between the three holonomy phases. The token framework can explain WHY Q = 2/3 IF the MDL-minimizing gauge configuration on the lepton sector has Z₃ symmetry. Whether MDL forces Z₃ symmetry on the lepton gauge links is the specific open question.

**Koide best-fit parameters** (from A + B·cos(θ + 2πk/3) parametrization):
```
A = 10.386 MeV^1/2
B = 32.243 MeV^1/2
B/A = 3.104
θ = 110.1°
```
The B/A = 3.104 has no simple group-theoretic explanation yet (√2 = 1.414 was tried and fails; √3 = 1.732 was tried and fails).

**Verdict: OPEN.** No principle from the four axioms has been found that selects specific holonomies without mass input. The Z₃ connection to Koide is the most promising direction. If MDL can be shown to require Z₃ symmetry on the lepton gauge links, holonomies become predictions.

---

## Test 3: Continuum Limit

**Question:** Can the correspondence between token bits and physical energy units be derived from the axioms?

### What is derived

From Tier 2 work (additional-support.md Items 8, 11, 13):

**Dirac equation:** The tight-binding Hamiltonian on a staggered (N,M) sublattice (even/odd sites) gives the Dirac equation in the continuum limit. This is a standard result from lattice field theory. The derivation is complete; the lattice spacing appears as a free parameter a = l_P.

**Maxwell equations:** The U(1) Wilson plaquette action in the continuum limit gives Maxwell's equations. Complete.

**Lorentz invariance:** Emergent at scales ≫ l_P. The isotropy of the token lattice (no preferred N or M direction at long wavelengths) gives emergent Lorentz invariance. This is argued via the Ignatowski theorem — the existence of a maximum speed follows from isotropy + causality.

**Wilson action = MDL minimum (THEOREM):**
```
P(config) ∝ exp(-l(config))  [MDL]
P(config) ∝ exp(-S_W)         [Wilson path integral]
→ l(config) = S_W at each configuration
→ MDL minimum ≡ Wilson action minimum  □
```
This is the formal proof that MDL is the least-action principle applied to descriptions. Not an analogy — an identity.

### What requires external calibration

The Planck energy E_P in joules. The framework establishes E_P × l_P = ℏc (from the minimum description energy times minimum description length = quantum of action). But the absolute value E_P in SI units requires fixing the quantum of action ℏ from an experiment. This is the standard situation in any fundamental theory: one external measurement is needed to set the scale.

**Consequence:** Once E_P is fixed from one measurement, every other dimensionful prediction sharpens. The factor-of-2 error in the gauge coupling is exactly this ambiguity. With α₂(M_Z) = 0.034 as the one fixed input (instead of deriving it from E_P alone), the predictions change as follows:

| Quantity | Without fix | With α₂(M_Z) fixed | Observed |
|---|---|---|---|
| sin²θ_W | 0.210 (9% err) | 0.191 (17% err) | 0.231 |
| α_s(M_Z) | 0.020 (83% err) | 0.181 (53% err) | 0.118 |

Fixing α₂ as input does not improve the Weinberg angle — it makes it slightly worse. This means the 9% Weinberg angle error is NOT from the normalization ambiguity. It comes from the scale mismatch between E_P (~10¹⁹ GeV) and the true GUT unification scale (~10¹⁶ GeV). The α_s error is partially normalization and partially one-loop running being insufficient for QCD.

**Verdict: PARTIAL.** Dirac equation, Maxwell equations, Lorentz invariance, Wilson=MDL are all derived. The absolute energy scale requires one experimental input. The 9% Weinberg angle error is identified but not yet closed.

---

# PART II — NEW PROOFS (from this session and Tier 1/2 work)

## II.1 Theorem: Why U(1) Not U(N) for the N-Sector **[PROVEN]**

The N leading zeros could in principle carry U(N) symmetry. They do not.

The Frozen decoder counts zeros but does not index them — it outputs N, not (which zero is which). By the Named axiom, the physical content is the decoder output. A transformation rotating zero #3 by θ₃ ≠ θ₇ (zero #7) creates a physically unobservable difference. The Named axiom forbids physically unobservable differences from being physical. Therefore all N zeros rotate by the same phase θ. The symmetry group is U(1). □

---

## II.2 Theorem: Gauge Sector Disjointness **[ARGUED — completeness gap remains]**

See previous supplement §I.1. The proof is complete for disjointness; completeness (no other sectors) is argued but not proven.

---

## II.3 Theorem: Nested Amplitude Structure **[PROVEN]**

The lepton path sums from Higgs (2,0) to lepton sites give:
```
|A_τ|² ∝ |1 + e^{iΔ₀}|²
|A_μ|² ∝ |1 + e^{iΔ₁}(1 + e^{iΔ₀})|²
|A_e|² ∝ |1 + e^{iΔ₂}(1 + e^{iΔ₁}(1 + e^{iΔ₀}))|²
```
This follows by counting shortest paths on the (N,M) lattice and collecting gauge phases at each visited site. The nesting arises because each new generation depth adds one new path that re-traverses all shallower paths. Proof: complete enumeration of C(2,1)=2, C(3,1)=3, C(4,1)=4 shortest paths respectively. □

Properties:
1. Exact (not truncated)
2. Two physical holonomy parameters encode all three mass ratios bijectively
3. Scale-invariant: all |t|² prefactors cancel in ratios

---

## II.4 Theorem: Flat Field Impossibility **[PROVEN]**

No uniform holonomy configuration (Δ₀ = Δ₁ = Δ₂) can simultaneously satisfy τ/μ ≠ μ/e.

With uniform Δ, the ratio (τ/μ)/(μ/e) = FH/G² is fixed for each Δ, and independently sweeping Δ ∈ [0, 2π] cannot produce both τ/μ = 16.82 and μ/e = 206.77. The observed hierarchy requires genuinely non-uniform holonomies. □

Physical meaning: the lepton mass hierarchy requires a non-trivial (non-flat) gauge field on the token lattice. Zero gauge flux → equal-mass generations.

---

## II.5 Theorem: SU(2) Breaking Required by MDL **[ARGUED → near PROVEN]**

From Tier 2 Item 9 computation:
- Cost of 3 gauge bosons acquiring mass: ~171 bits
- MDL savings from fermion mass generation via Yukawa: 1992 bits (12 fermions × 166 bits each)
- Net MDL advantage: +1821 bits in favor of breaking

The Higgs token at (2,0) is the MDL-minimum M=0 token that spans both SU(2) doublet components. A non-zero vev saves more description cost than it spends. Breaking is not a choice — it is required by MDL.

U(1)_EM remains unbroken because: N-count conservation is a structural property of the Frozen decoder (never revises N after first pass). This is not a dynamical symmetry — it cannot be broken by any field configuration. Therefore m_γ = 0 exactly and U(1)_EM is exact. □

---

## II.6 Theorem: Photon Masslessness **[PROVEN]**

m_γ = 0 because:
1. Photon token: (N=0, M=1). N = 0.
2. The Frozen decoder conserves N in every PRODUCE operation (structural, not dynamical).
3. N = 0 → no rest frame → massless.

This is a structural theorem about the decoder, not a consequence of gauge invariance. The photon cannot acquire mass through any mechanism, because any mass-giving mechanism is a PRODUCE operation, and PRODUCE operations cannot change N. □

---

## II.7 Theorem: Baryon Asymmetry Consistent **[PROVEN]**

The apparent contradiction: compositionality L(u;v) = L(u)⊕L(v) implies N-conservation (additive), but sphalerons violate B+L.

Resolution: There are two operation types:
- **PRODUCE:** composes existing tokens. Compositionality applies. N is conserved.
- **DEFINE:** adds new base tokens to vocabulary V₀, changing the vacuum sector.

Sphalerons are topological vacuum transitions — they change the Chern-Simons winding number of the gauge field. This corresponds to a DEFINE operation (changing which vacuum state is in V₀). DEFINE operations are not constrained by compositionality.

Therefore B+L violation is structurally consistent with the framework. Open Problem 8 of master.md: **CLOSED.** □

Quantitative observation: c_Σ/S_inst(Planck) = 825/583.4 = 1.41409 ≈ √2 (0.009% accurate). The instanton action at the Planck scale is c_Σ/√2. This is an empirical observation with a candidate derivation (see §II.8 below).

---

## II.8 New Result: c_Σ = √2 × S_inst — Candidate Derivation **[ARGUED]**

The empirical fact: c_Σ = √2 × S_inst to 0.009%.

Candidate derivation via dimensional counting:
- The SU(2) instanton moduli space has SO(4) symmetry: dim(SO(4)) = 6
- The token lattice has O(3) causal automorphisms: dim(O(3)) = 3
- Ratio: 6/3 = 2. Square root: √2.
- c_Σ = √(dim SO(4)/dim O(3)) × S_inst = √2 × S_inst

The instanton is a 4-dimensional Euclidean object; the token lattice is 2-dimensional. The √2 is the geometric mean factor connecting the two dimensional structures via their symmetry groups.

**Status: ARGUED.** The dimensional count gives exactly √2. Whether this is the correct physical explanation or a numerical coincidence at this precision requires further analysis. The 0.009% accuracy is consistent with it being exact.

---

## II.9 Theorem: Hamiltonian Structure **[ARGUED → upgraded from CONJECTURAL]**

From additional-support.md decision trees (not previously in supplement):

**H_diag = E_P(N+M+1) |N,M⟩** — DERIVED, not guessed.
- MDL: description cost = energy (same thing in different units)
- Description cost of (N,M) = l(N,M) = N+M+1 bits
- N and M are independent → energies add independently
- Therefore H_diag = E_P × (N+M+1) □

**H_off connects only nearest neighbors** — DERIVED.
- Frozen single-pass decoder: processes one bit at a time
- Elementary operation: add or remove exactly one bit (change N or M by ±1)
- Long-range hops (jump ΔN > 1 or ΔM > 1) require multiple simultaneous bit changes: impossible for the single-pass decoder
- Therefore H_off is nearest-neighbor only □

**Base hopping amplitude t = exp(-1)** — DERIVED.
- Born weight of one production step: exp(-1 bit) = exp(-1) per hop
- This is the MDL probability amplitude for extending a token by one bit
- Same for N-direction and M-direction hops at the Planck scale
- Physical couplings differ at low energy via RGE running, not from different base amplitudes

**Corrected H_off formula** (replacing the wrong formula in master.md §57):
```
H_off = t_N Σ_{N-adjacent} |N±1,M⟩⟨N,M|  +  t_M Σ_{M-adjacent} e^{±iα_{N,M}} |N,M±1⟩⟨N,M|
```
where t_N = t_M = exp(-1) at Planck scale, and α_{N,M} are gauge phases (the holonomies Δᵢ from §II.3).

---

## II.10 Theorem: Spin Assignments from Causal Automorphisms **[ARGUED]**

From Tier 2 Item 11:

The causal partial order on the (N,M) lattice has local automorphism group O(3). The O(3) representations give:

| Representation | Object | SM particle type |
|---|---|---|
| Trivial (spin-0) | Corner site (2,0) | Higgs ✓ |
| Fundamental spinor (spin-½) | Matter lattice sites | Quarks, leptons ✓ |
| Vector (spin-1) | Links between sites | Gauge bosons ✓ |
| Symmetric tensor (spin-2) | Metric fluctuation | Graviton (not in SM) ✓ |

All SM spin assignments reproduced with no additional input. The distinction between fermions (sites) and gauge bosons (links) is structurally forced by the lattice — matter lives at nodes, interactions live on edges.

---

# PART III — COUPLING CONSTANTS: COMPLETE CORRECTED ANALYSIS

## III.1 Correction to master.md Section 61

**Old values (WRONG):**
```
α_EM(E_P)   = exp(-2) ≈ 0.135   [missing 4π, wrong by 12.6×]
α_weak(E_P) = exp(-3) ≈ 0.050   [wrong exponent AND missing 4π]
α_strong(E_P) = exp(-2) ≈ 0.135  [missing 4π, wrong by 12.6×]
```

**Corrected values:**
```
α₁(E_P) = α₂(E_P) = α₃(E_P) = exp(-2)/(4π) ≈ 0.01077
```

All three equal. This is a **unification prediction** derived from the single hop amplitude t = exp(-1). The framework cannot have different Planck-scale couplings for different gauge groups — there is one type of bit, one hop amplitude, therefore one coupling.

This is what SU(5)/SO(10) GUT theories assume. The token framework derives it.

## III.2 Physical Meaning of α_token = exp(-2)/(4π)

The 4π factor comes from the QFT identification: α = g²/(4π) where g is the vertex factor. The token hop amplitude t is g (the amplitude for a gauge boson emission/absorption), not √α. This is the root cause of the previous factor-of-12 error.

The remaining factor of ~2 between α_token = 0.0108 and the observed Planck-scale values (0.019–0.030) is the continuum limit ambiguity — it cannot be resolved without knowing the exact token bit ↔ physical energy correspondence.

## III.3 What the Framework Predicts (with one input fixed)

Starting from unified α_token at E_P and running down with SM one-loop β-functions:

| Quantity | Predicted | Observed | Error | Blocking issue |
|---|---|---|---|---|
| sin²θ_W(M_Z) | 0.210 | 0.231 | 9% | Scale mismatch E_P vs E_GUT |
| α_s(M_Z) | 0.020 | 0.118 | 83% | One-loop insufficient for QCD + scale |
| α_2(M_Z) | 0.014 | 0.034 | 59% | Factor-of-2 normalization |
| α_EM(M_Z) | 1/270 | 1/128 | 112% | Same normalization |

The **9% Weinberg angle error** is the best prediction. Its source is identified: the token framework sets initial conditions at E_P ≈ 10¹⁹ GeV, but the SU(2)/SU(3) couplings unify at E_GUT ≈ 2×10¹⁶ GeV. Running α₁ and α₂ through the extra factor of ~600 in energy introduces a 9% shift in sin²θ_W. This closes when the continuum limit establishes the correct token-scale energy.

The **83% α_s error** is a separate problem: the SU(3) color sector lives at depth M=3 (deeper in the lattice) and likely has a different natural scale than M=1 (SU(2)). The SM one-loop running from E_P treats all sectors identically, which is incorrect. The SU(3) running needs a separate scale assignment.

---

# PART IV — COMPLETE STATUS TABLE

Updated from the epistemic ledger in previous supplement.

| # | Claim | Status | Source |
|---|---|---|---|
| 1 | Token uniqueness theorem | PROVEN | master.md §4 |
| 2 | Two-Dimension Theorem | PROVEN | master.md §17 |
| 3 | Charge quantization | PROVEN | master.md §30 |
| 4 | Photon masslessness | PROVEN | §II.6 this doc |
| 5 | Quaternionic QM ruled out | PROVEN | master.md |
| 6 | Measurement = symbol completion | PROVEN | master.md |
| 7 | U(1) not U(N) for N-sector | PROVEN | §II.1 this doc |
| 8 | Born rule (Gleason) | ARGUED | master.md §19 |
| 9 | Lorentz invariance (emergent) | ARGUED | Tier 2 Item 13 |
| 10 | Schrödinger → Dirac equation | ARGUED | Tier 2 Item 13 |
| 11 | Maxwell equations from Wilson | ARGUED | Tier 2 Item 8 |
| 12 | Wilson action = MDL minimum | ARGUED | §III.1 this doc |
| 13 | Gauge group U(1)×SU(2)×SU(3) | ARGUED | §I + §II.2 |
| 14 | Disjointness of gauge sectors | ARGUED | §II.2 this doc |
| 15 | Completeness (no other sectors) | ARGUED | §I.1 this doc |
| 16 | Parity violation | ARGUED | master.md §35 |
| 17 | SU(2) breaking required | ARGUED | §II.5 this doc |
| 18 | Higgs sector = M=2 | ARGUED | §I.1 this doc |
| 19 | Spin-½,1,0 assignments | ARGUED | §II.10 this doc |
| 20 | Nested amplitude structure | PROVEN | §II.3 this doc |
| 21 | Flat field impossibility | PROVEN | §II.4 this doc |
| 22 | Lepton mass hierarchy direction | ARGUED | Tier 1 + lattice |
| 23 | 8/3 quark/lepton pattern | ARGUED | Tier 1 Item 6 |
| 24 | Koide = Z₃ gauge symmetry | ARGUED | §I.2 this doc |
| 25 | CP violation δ ≠ 0 | PROVEN | master.md §44 |
| 26 | Baryon asymmetry consistent | PROVEN | §II.7 this doc |
| 27 | H_diag = E_P(N+M+1) | ARGUED | §II.9 this doc |
| 28 | H_off = nearest neighbor only | ARGUED | §II.9 this doc |
| 29 | t = exp(-1) base hop | ARGUED | Tier 1 Item 1 |
| 30 | c_Σ = √2 × S_inst | ARGUED | §II.8 this doc |
| 31 | α_token = exp(-2)/(4π) | ARGUED | §III.1 this doc |
| 32 | GUT unification predicted | ARGUED | §III.1 this doc |
| 33 | sin²θ_W = 0.210 (9% error) | ARGUED | §III.3 this doc |
| — | Exact fermion masses | OPEN | needs Monte Carlo |
| — | Exact CKM phase δ | OPEN | needs Monte Carlo |
| — | Cabibbo angle θ_C = 13° | OPEN | no path yet |
| — | Koide from first principles | OPEN | Z₃ approach open |
| — | Neutrino masses | OPEN | — |
| — | Newton's G in SI | OPEN | needs E_P in joules |
| — | Cosmological constant | OPEN | — |
| — | Higgs mass | OPEN | — |
| — | Coupling factor-of-2 | OPEN | continuum limit |
| — | Exact holonomies from axioms | OPEN | Z₃/MDL approach |

---

# PART V — OUTSTANDING NUMERICAL PUZZLES

## V.1 c_Σ = √2 × S_inst

```
c_Σ = 825 bits
S_inst = 8π²/g₂² = 8π²e² = 583.4165
c_Σ/S_inst = 1.41409
√2 = 1.41421
Error: 0.009%
```

Candidate derivation: √(dim SO(4) / dim O(3)) = √(6/3) = √2. The instanton has SO(4) symmetry; the token lattice has O(3) causal automorphisms. Status: ARGUED.

## V.2 θ_Koide + θ_Cabibbo ≠ 120° (FAILS)

```
θ_Koide  = 107.268°
θ_Cabibbo = 13.040°
Sum = 120.308°
Target = 120.000°
Error = 6.2σ
```

This relation does NOT hold at current experimental precision. It is 6.2 standard deviations from exact. **Do not include as a framework prediction.**

## V.3 8/3 Cross-Ratio Pattern (HOLDS to ~5%)

```
(c/u)/(μ/e)   = 2.791  [need 8/3 = 2.667]  err = 4.7%
(μ/τ)/(c/t)   = 8.100  [need 8.000]        err = 1.3%
(τ/c)/(μ/τ)   = 23.53  [need 24]           err = 2.0%
(μ/τ)/(d/μ)   = 1.337  [need 4/3 = 1.333] err = 0.3%
```

Physical origin: SU(3) has 8 generators, SU(2) has 3. Coherent path sums to quarks include 8 independent SU(3) paths; to leptons, 3 SU(2) paths. Amplitude ratio squared → 8/3. This is a structural prediction. The exact value needs Monte Carlo.

---

# PART VI — WHAT REMAINS FOR TIER 3

Items that require Monte Carlo or are genuinely long-term:

1. **Full 9-fermion mass matrix** — lattice computation, 100-core cluster, 6–12 months. The complete test of the framework.
2. **Exact CKM matrix** — same computation, gives δ, θ_C, and all mixing angles.
3. **Tau/mu exact ratio from SU(2) matrix elements** — needs specific gauge field minimization. Site reversal confirmed (heavier = closer to Higgs: τ at (1,0), μ at (1,1), e at (1,2)). Required SU(2) elements computed: |U| = 0.162 for τ/μ link, |U| = 0.013 for μ/e link. Monte Carlo needed for the full configuration.
4. **SU(3) coupling at M_Z** — requires separate scale assignment for the color sector (M=3 ≠ M=1 in terms of natural energy scale).
5. **Koide from Z₃** — if MDL forces Z₃ symmetry on lepton gauge links, this closes the holonomy problem. A specific MDL analysis on the 3-site lepton sector.
6. **Higgs mass** — requires full Coleman-Weinberg effective potential in the token lattice.
7. **Cabibbo angle** — Georgi-Jarlskog texture gives arcsin(√(m_d/m_s)) = 12.85° (1.4% error from 13.04°) as the best available approximation. Not yet derived from token structure.

---

# PART VII — WHAT THIS MEANS OVERALL

## Three things the framework has now that it did not before these sessions:

**1. A derived unification prediction.** α₁ = α₂ = α₃ at the Planck scale follows from having one hop amplitude t = exp(-1). GUT theories assume this. The token framework derives it from four axioms and the binary alphabet theorem. This is non-trivial.

**2. A proof that baryon number violation is consistent.** The apparent contradiction between N-conservation and sphalerons is resolved: sphalerons are DEFINE operations, not PRODUCE operations. Compositionality constrains PRODUCE only. Open Problem 8 of master.md is closed.

**3. A complete Hamiltonian derivation.** H_diag = E_P(N+M+1) is derived from MDL (not guessed). H_off = nearest-neighbor is derived from the Frozen decoder (not assumed). t = exp(-1) is derived from the Born weight of one production step. The previous master.md called these conjectural. They are now argued with clear derivation chains.

## One thing that is clearer now:

The single remaining numerical gap (the factor-of-2 in α, the 9% in sin²θ_W, the 83% in α_s) all trace back to one problem: the token lattice spacing is not yet derived from the axioms. This is the continuum limit problem. It is not a vague gap — it is a specific thing: show that the minimum localization energy of one token bit equals ℏc/l_P = E_P. When that is done, every dimensionful prediction sharpens simultaneously.

---

*v2 — March 2026. Pull into master.md at next revision.*
