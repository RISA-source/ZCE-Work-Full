# The (N,M) Lattice Framework — Core Summary
## Version 11.0

**Rishi Saraff | Herald College Kathmandu | 2026**

*Entry point. Read this first. Detailed proofs in proofs.md.*

---

## The Central Question

What is the minimum structure required for something to be stably and distinctly itself?

Not a physics question. A question about the minimum conditions for a self-identifying system to exist. The answer turns out to have the structure of the Standard Model gauge group. This is either a deep coincidence or something more. The framework is an attempt to determine which.

---

## The Four Axioms

A self-identifying system must satisfy all four. Independence confirmed by counterexamples.

**Named:** Every distinguishable state has a unique, recoverable label.

**Frozen:** The label is intrinsic — readable in a single left-to-right pass, no external data. *Named+Learnable alone don't give Frozen: integer labels {1,2,3,...} satisfy both but are not self-delimiting in binary.*

**Productive:** Every possible state can be produced.

**Learnable:** New states can be systematically produced from existing ones.

**Minimality (meta-axiom):** Two systems producing identical physics are the same system. Use the minimal representative.

---

## What the Axioms Force (Tier 1 — Proven)

Starting from the four axioms alone:

**Binary alphabet (P1):** Exactly two symbols {0,1}.

**Unique token (P3):** The encoding [0^N 1^M 0] — N leading zeros, M ones, terminating zero — is the unique minimal binary encoding. The decoder is a 2-counter machine (not a finite-state machine; the language is not regular).

**Two parameters (P2):** Exactly two irreducible intrinsic parameters N and M. N = identity index. M = depth index.

**Token count (P5):** At each length L = N+M+1, there are exactly L distinct tokens.

**Three non-self-similar levels (P7):** The symmetry groups of the L-dimensional complex spaces are SU(L). Exactly three are non-self-similar: L=1 giving U(1), L=2 giving SU(2), L=3 giving SU(3).

**Self-similarity at L≥4 (P8):** All SU(L≥4) representations decompose into SU(3)×SU(2)×U(1) representations. Pure Lie group theory.

These seven results hold regardless of any physical assumption.

---

## The Identification (P22) — The Load-Bearing Wall

**THEOREM:** If physical particles satisfy conditions D1–D4, then the space of particle species is isomorphic to a subset of the (N,M) token lattice, and the gauge symmetry is SU(3)×SU(2)×U(1) as a direct product.

**PHYSICAL HYPOTHESIS:** Standard Model particles satisfy D1–D4.

D1 = Named, D2 = Frozen, D3 = Productive, D4 = Learnable for particle species.

This hypothesis is physically well-motivated (quantum numbers are superselected, gauge-invariant, the S-matrix is complete, all particles are producible) but is not formally proven from deeper axioms. The gap at D2 — that quantum numbers map to Frozen self-delimitation — is the central open problem.

**If P22 fails, all physics results fall.** Only the seven Tier 1 math results survive.

---

## What Follows Given P22 (Tier 2 — Physics Results)

**Product group (P7b):** G = U(1) × SU(2) × SU(3) as a DIRECT PRODUCT. L is a superselection quantum number (Frozen → L frozen → no inter-sector mixing → direct product, not semidirect or unified). This rules out SU(5), SO(10), all GUTs.

**Charge values (P13) — THEOREM:** {0, −1, +2/3, −1/3} are the unique solution to all four anomaly cancellation conditions given the gauge group. No SM data used. All four conditions verified explicitly.

**sin²θ_W = 3/8 (P25) — PROVEN:** Trace formula sin²θ_W = Σ(T₃²)/Σ(Q²) = 2/(16/3) = 3/8. Uses only doublet structure (P7) and charge values (P13). No GUT embedding, no equal-coupling assumption. Running to m_Z gives 0.229; observed 0.2312; error 0.9%.

**Strong CP solved (P18):** θ_QCD = 0 from two arguments: (1) Euclidean weights e^{−L} are real positive → no θ term; (2) Yukawa matrix is real symmetric by construction → det(Y) real → arg(det Y) = 0.

**Proton stable at all orders (P7b):** No gauge boson with ΔL≠0 exists. Proton decay requires ΔL=8 gauge bosons — forbidden exactly, not just suppressed.

**3 generations (P21):** Lower bound from CP violation requirement (≥3). Upper bound from LEP constraints (4th generation lepton would appear in Z decays).

**No SUSY (P10+P7b):** Same N → same η = (−1)^N → same statistics. Superpartner with same charges needs different spin but same N. Impossible.

**No extra dimensions (Named):** KK towers have identical gauge quantum numbers but different masses. Named forbids this — distinct entities must have distinct labels.

**Yang-Mills dynamics (T3):** Frozen → intrinsic labels → local gauge invariance (given Einstein locality) → covariant derivative → Yang-Mills action as unique minimal renormalizable gauge-invariant kinetic term (given D=4).

---

## What Is Not Yet Derived (Tier 3)

**Higgs mass:** λ = e^{−2} conjecture gives m_H = 128 GeV at tree level. Tree-level prediction is 16σ from the measured pole mass. At 1-loop, tension reduces to ~2.6σ. The identification was found post-hoc. MOTIVATED CONJECTURE, not resolved.

**Spacetime dimensions:** Named → no CTCs (real result). This does not imply D_time=1. Ehrenfest motivates D_space=3 but Learnable doesn't formally require stable atoms. Spacetime is not derived.

**Absolute gauge couplings:** Only sin²θ_W (a ratio) is derived. The absolute values g₁, g₂, g₃, α_EM are open.

**Fermion masses:** The M-values within each generation are initial conditions. 8 free parameters remain. A fifth axiom is required (candidate: Fibonacci recursion L(g+2)=L(g+1)+L(g)).

**CKM matrix:** Structure correct (diagonal dominance, 1 phase). Cabibbo angle |V_us| = e^{−3/2} = 0.2231 (observed 0.2245, 0.6%) if ξ=2. The derivation of ξ=2 from the framework is pending — if it works, this is a zero-parameter prediction. |V_cb|, |V_ub|, δ need fermion M-values.

---

## The Honest Position

This framework shows that four natural axioms about distinguishability force U(1)×SU(2)×SU(3) as a direct product gauge group, the SM charge values, sin²θ_W = 3/8, proton stability, θ_QCD = 0, three generations, no SUSY, no extra dimensions, and Yang-Mills dynamics — given that particles satisfy the four axioms.

This is a significant structural result. It is not a complete theory of physics.

**What would complete it:**
1. Formal proof that particles satisfying physical distinguishability must satisfy D1–D4 (P22)
2. Derivation of ξ=2 to make Cabibbo a zero-parameter prediction
3. Fifth axiom giving generation lengths 5, 8, 13
4. Derivation of absolute gauge couplings
5. Connection of T=137 to α_EM

---

## Document Map

| Document | Contents |
|---|---|
| framework_core.md | This file. Overview, structure, honest position. |
| proofs.md | All proofs, all retractions, all dead ends. v11.0. |
| proofs_v8_backup.md | Previous version (v8.0) for reference. |
| M2_symmetry_calculation.md | Failed M-depth approaches (historical). |
| P6_decision_map.md | Historical decision tree for P6. |

---

*Rishi Saraff | Herald College Kathmandu | 2026 | v11.0*

---

## Session 15 Update

**New results:**

**T5 (Poincaré group) [★★★☆☆]:** Named+Productive → relativity principle (no preferred frame). Named → isotropy+homogeneity. Frozen → time homogeneity + finite signal speed. Named+T4 → Zeeman theorem → Poincaré ⊗ dilations. Named (integer L) → dilations broken → Poincaré exactly. Gaps stated: relativity principle step and c<∞ step need formalization.

**P22 tightened [★★★★☆]:** The chain axioms → P7b → P13 → P22 is non-circular. P22 reduces to: "the SM has the gauge group P7b derives, with the charges P13 proves." The identification is nearly a corollary. Remaining gap: physical correspondence principle (N = SU(2) index, M = generation index).

**α = 1/137:** No mechanism found. Genuinely open. The running of α is governed by SM charges (which the framework derives) but the absolute value of α(0) cannot be extracted from token counting alone.

**λ = e^{-2}:** No derivation found. Natural labeling (coupling = token weight of mediator) but not a proof. Stays Tier 3.

**Fermion mass ratios:** Order-of-magnitude predictions from Fibonacci L-values match observations. Exact values blocked by O5 (M-values problem).
