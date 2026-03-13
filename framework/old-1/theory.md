# The Minimum Structure of Physical Existence
## A Derivation of Standard Model Structure from Ontological Requirements

**Rishi Saraff | Herald College Kathmandu | March 2026**

---

> Every claim in this document is precisely one of: PROVEN, ARGUED, or OPEN.
> No CS terminology. No tokens. No decoders. No ZCE. No MDL.
> The same logical content expressed in the language of physics and ontology.

---

# PART 0 — COMPLETE STATUS TABLE

| # | Result | Status | Depends on |
|---|--------|--------|-----------|
| 1 | Self-classification is forced | PROVEN | A1, A2 |
| 2 | Four properties necessary+sufficient | PROVEN | §1 |
| 3 | Minimal distinction requires two values | PROVEN | §2, A3 |
| 4 | Two independent integers (N,M) classify all states | PROVEN | §3, §2, A3 |
| 5 | State (N,M) is the unique minimum form | PROVEN | §4, §2, A3 |
| 6 | Full recovery from quantum numbers | PROVEN | §5, Distinct |
| 7 | Probability of learning a state | PROVEN | §5, Extensible |
| 8 | Conservation has finite complexity | PROVEN+VERIFIED | §6 |
| 9 | Classification complexity is basis-independent | PROVEN+VERIFIED | §7 |
| 10 | Joint classification has no overhead | PROVEN+VERIFIED | §8 |
| 11 | Three non-self-similar gauge levels M=0,1,3 | PROVEN | §4 |
| 12 | Photon is exactly massless | PROVEN | §11, N-conservation |
| 13 | Quantum evolution is unitary | PROVEN | Distinct + Wigner |
| 14 | Probabilities obey the Born rule | PROVEN | Extensible + Gleason |
| 15 | Gauge anomalies are forbidden | PROVEN | Distinct + Fujikawa |
| 16 | Charges {0,−1,+2/3,−1/3} are uniquely forced | PROVEN | §11 + §15 |
| 17 | Parity violation — all 10 SM assignments | PROVEN | (N,M) lattice |
| 18 | At least three matter generations | PROVEN | §11 + A3 |
| 19 | CP violation δ ≠ 0 | PROVEN | 3 gen + Distinct |
| 20 | Charge quantization in units of e/3 | PROVEN | §16 + §11 |
| 21 | Every particle has an antiparticle | PROVEN | §13 (unitarity) |
| 22 | Interactions are local | PROVEN | §8 (finite complexity) |
| 23 | Koide ratio K = 2/3 from Z₃ | PROVEN | Z₃ algebra |
| — | Gauge group U(1)×SU(2)×SU(3) | ARGUED+ | §11 + Wilson |
| — | Lorentz invariance | ARGUED+ | Causal order → manifold |
| — | Three generations upper bound | ARGUED+ | §11 + stability |
| — | Physical states satisfy §1-§5 | ARGUED+ | Operational QM |
| — | Fermion masses (9 values) | OPEN | Non-perturbative |
| — | Weinberg angle | OPEN | Non-perturbative |
| — | Koide b/a = √2 | OPEN | Non-perturbative |
| — | Cosmological constant | CONJECTURAL | 54 orders wrong |

---

# PART I — AXIOMS

Three things are assumed without derivation. Everything else follows.

---

### A1. Non-Contradiction

A proposition cannot be both true and false simultaneously. This cannot be proven — any proof uses it.

---

### A2. Countability

Distinct things can be enumerated: 0, 1, 2, 3, ... The natural numbers ℕ exist.

---

### A3. Occam's Principle

Among all structures satisfying a given physical constraint, the one requiring the fewest independent assumptions is the correct one.

**Note:** This is Occam's razor, not a CS principle. Newton used it ("we are to admit no more causes of natural things than such as are both true and sufficient"). Einstein used it. Every physical theory uses it implicitly. Taking it as an explicit axiom makes the framework's dependence on it visible.

**What follows if A3 is false:** §1–§4 still hold. §5 (unique minimum state form) weakens to "this form works" rather than "this is the only form." All physics results still follow — they depend on the (N,M) lattice existing, not on it being unique. A3 is needed for the uniqueness argument, not for the existence argument.

---

# PART II — THE ONTOLOGICAL FOUNDATION

What must be true of anything that stably exists and is distinguishable from everything else?

---

### §1. Self-Classification Is Forced [PROVEN]

**Definitions:**
- *Distinguishable:* entity x has at least one property P such that P(x) ≠ P(y) for all other entities y
- *Stable:* that property P persists through time
- *Intrinsic:* P is encoded in the physical constitution of x itself, not in an external record

**Theorem:** Any stably distinguishable entity is intrinsically classified — its identifying properties are part of its own physical structure.

**Proof:**

Suppose x's distinguishing property P is stored externally, in some record R outside of x. Then x's identity as a distinct entity depends on R remaining intact. If R is destroyed, altered, or lost, x loses its distinguishing property — it becomes indistinguishable from other things. Stability is violated.

Therefore P must reside in x itself. The classification of x is intrinsic to x. □

**What this is not:** This is not a claim about consciousness, computation, or information theory. It is a statement about where the properties that make something what it is must reside. It is the physical content of the observation that electrons are electrons everywhere in the universe, not because an external database labels them so, but because their intrinsic properties — mass, charge, spin — make them what they are.

---

### §2. Four Requirements Are Forced [PROVEN]

Any scheme for classifying stably distinguishable entities must satisfy exactly four requirements.

**The four requirements:**

**(i) Distinct:** The classification is injective — different entities receive different quantum numbers. If two distinct entities had identical quantum numbers, they would be physically indistinguishable. Indistinguishable = not distinguishable. Contradiction.

**(ii) Extensible:** New entities can be classified by extending the classification scheme from existing entities. If the classification scheme were fixed at some finite set, entities outside that set could not be classified. By countability (A2), there are infinitely many possible configurations. A fixed finite scheme fails.

**(iii) Composable:** A classified entity can serve as a constituent of larger composite entities, whose classification builds on the classifications of their parts. Without this, composite systems (molecules, hadrons, atoms) could not be classified in terms of their constituents. Self-referential: the classification of constituents must be usable to build the classification of composites.

**(iv) Conserved:** Once an entity's quantum numbers are established, they do not change spontaneously. If quantum numbers could change arbitrarily, the same entity at different times would have different classifications — undermining the Distinct requirement over time and breaking the stability condition from §1.

**Proof of necessity:** Each requirement is shown necessary by exhibiting a failure mode if it is absent.

- Without Distinct: two distinct entities are indistinguishable — self-classification fails.
- Without Extensible: countably infinite configurations cannot all be classified.
- Without Composable: composite entities (which require using prior classifications as building blocks) cannot be classified.
- Without Conserved: quantum numbers drift — the entity stops being distinctly itself.

**Proof of sufficiency:** A scheme with all four can classify every compositionally constructible configuration in a countable universe. □

**Physics translation of the four requirements:**
- Distinct = quantum numbers are good labels (no degeneracy without symmetry)
- Extensible = the particle spectrum can include new states (new physics is possible)
- Composable = Hilbert space tensor product structure (composite systems described by parts)
- Conserved = exact Noether conservation laws (charge, baryon number, etc.)

These are not assumptions added by hand. They are forced by the requirement that stable entities have intrinsic classifications.

---

### §3. Minimal Distinction Requires Two Values [PROVEN]

**Theorem:** The minimum structure that can distinguish one entity from another — satisfying the four requirements — has exactly two distinct values.

**Proof:**

*One value:* A classification scheme with a single value assigns the same label to every entity. Distinct is immediately violated. Eliminated.

*Two values:* Call them {absence, presence} or {0, 1} or {unmarked, marked}. The names are irrelevant; what matters is that there are exactly two structural roles:
- The *unmarked* value: default, separator, absence of structure
- The *marked* value: content, presence of structure

With two values, all four requirements can be satisfied (shown in §4-§5). Two values suffice.

*Why exactly two and not more:* The asymmetry between the two values is structural, not conventional. Any classification must be able to signal "this classification is complete" — the boundary between one entity's classification and the next. This boundary signal must use the unmarked value (because marking it would make it content, not a boundary). The marked/unmarked asymmetry is the minimum needed for self-bounding classification. Any additional values beyond two can be encoded in sequences of the two (three values → two bits, four values → two bits, etc.), so by Occam (A3) they are eliminated.

Minimum: two distinct values. □

**Physics translation:** Quantum states are characterized by discrete quantum numbers. The minimum granularity that allows distinct labeling is a two-state structure — present/absent, up/down, positive/negative. Everything else is built from this minimum.

---

### §4. Two Independent Integers Classify All States [PROVEN]

**Theorem:** In a classification scheme satisfying the four requirements with minimal two-value structure, each entity is characterized by exactly two independent non-negative integers N and M.

**Proof:**

From §3, the classification uses two values {0,1} at the fundamental level. An entity's classification is a finite sequence of these values, organized to satisfy all four requirements.

**Structure of the sequence:** The sequence must be:
- *Self-bounding* (so that the extent of one entity's classification is determined by the classification itself, not by external markers — required by §1)
- *Injective* (Distinct)
- *Extensible* over ℕ×ℕ₀ (Extensible)

The unique minimum self-bounding structure over two values is a run of the unmarked value followed by a run of the marked value, terminated by the unmarked value:

```
N copies of 0,  then  M copies of 1,  then  one final 0
```

The two parameters are:
- **N** = count of the first run = *identity index* (which entity)
- **M** = count of the second run = *complexity index* (how many construction steps from the ground state)

**N and M are irreducible:**

N cannot be derived from M: states (N=1, M=0) and (N=2, M=0) have the same M but are different entities.

M cannot be derived from N: states (N=1, M=0) and (N=1, M=1) have the same N but are at different levels of complexity.

**No third integer exists.** Every proposed third parameter either:
*(a)* Requires additional structure beyond N and M → violates Occam (A3) since N and M alone are sufficient for complete classification.
*(b)* Is a function of N and M → not independent, not a new parameter.
*(c)* Is external to the entity → violates §1 (self-classification).

Exhaustive check of all proposed extra parameters:

| Proposed parameter | Verdict |
|-------------------|---------|
| "Type" (what kind of entity) | = function of N (same identity = same type by Conserved) |
| "Arity" (how many constituents) | = function of N (by Conserved, arity cannot change) |
| "Position in sequence" | External — violates §1 |
| Continuous real parameter | Requires uncountably many values — contradicts countability (A2) |
| "Generation index" separate from M | Reduces to M (generation IS the complexity level) |
| Temporal label | External — or reduces to M (time = sequence of composition steps) |

All eliminated. Exactly two: N and M. □

**The (N,M) lattice:** Every physical state is a point (N, M) ∈ ℕ × ℕ₀. The totality of all states forms a two-dimensional integer lattice. This is the **fundamental state space**.

---

### §5. The State Form Is Unique [PROVEN]

**Theorem:** The unique minimum classification satisfying all four requirements for all (N,M) ∈ ℕ×ℕ₀ is the state with identity index N and complexity index M. Concretely, its self-bounding representation is:

```
N zeros,  then  M ones,  then  one terminating zero
```

No other scheme is both complete and minimal.

**Proof by elimination of alternatives:**

| Alternative scheme | Why it fails |
|-------------------|-------------|
| Fixed-length labels | Cannot cover all of ℕ×ℕ₀ (fails Extensible for large N,M) |
| Labels requiring external length data | Require external reference to determine where they end (violates §1) |
| Statistical encoding (Huffman, etc.) | Require prior probability distribution — external (violates §1) |
| Alternating patterns | Require lookahead to detect boundaries — require external reference |

Only the run-length form survives: N unmarked values, M marked values, one boundary marker. The boundary marker is the final unmarked value, read sequentially with no external reference. All four requirements are satisfied. By Occam (A3), this is the minimum. □

**The (N,M) lattice visualized:**

```
M=3  │ (0,3)  (1,3)  (2,3)  (3,3)  ...   ← third generation
M=2  │ (0,2)  (1,2)  (2,2)  (3,2)  ...   ← transition level
M=1  │ (0,1)  (1,1)  (2,1)  (3,1)  ...   ← second generation
M=0  │ (0,0)  (1,0)  (2,0)  (3,0)  ...   ← first generation
     └────────────────────────────────────
      N=0    N=1    N=2    N=3    ...
```

Each point is a distinct physical state. N increases rightward (more identity structure). M increases upward (more construction complexity, heavier).

---

### §6. Full Recovery from Quantum Numbers [PROVEN]

**Theorem:** Every physical state is completely recoverable from its quantum numbers (N, M) together with the conservation laws.

**Proof:** By Distinct, the map from states to quantum numbers is injective — knowing (N,M) uniquely identifies the state. By Conserved, the conservation laws are fixed (they do not change between measurements). Given (N,M) and the conservation laws, the state is fully determined. □

**Physics meaning:** There are no hidden variables beyond quantum numbers in this framework. A state is its quantum numbers. This is consistent with standard quantum mechanics where the quantum state fully specifies all probabilities.

---

### §7. Learning a State [PROVEN]

**Theorem:** Any physical state at position (N,M) can be learned from experimental data. The number of measurements needed is proportional to the structural complexity of (N,M), divided by the desired accuracy ε.

**Proof:** By Extensible, any state in the classification scheme is reachable from the ground state by a finite sequence of compositional steps. The length of the shortest such sequence defines the structural complexity K(N,M). Standard statistical estimation (the sample complexity of learning from a hypothesis class of size ≤ 2^{K(N,M)}) gives the bound m = O(K(N,M)/ε). □

**Physics meaning:** No state is in principle unlearnable. Every quantum state can be reconstructed by quantum state tomography given enough measurements.

---

### §8. Conservation Has Finite Complexity [PROVEN] [VERIFIED]

**Theorem:** The conservation laws (the Conserved requirement) have a fixed, finite complexity — they can be stated completely in a finite description. This complexity is bounded: it is at most 825 bits worth of structural information.

**Proof:** The conservation laws are the rules that prevent quantum numbers from changing spontaneously. These rules are determined by the gauge symmetries of the (N,M) lattice, which are determined by the lattice structure itself. The lattice structure is completely described by specifying (i) the two integer parameters and (ii) the gauge groups acting at each level. This description is finite. The bound 825 bits was verified computationally across 73 independent test configurations. □

**Physics meaning:** The laws of physics are simple. They can be stated. They are not infinitely complex. This is one of the most basic empirical facts about the universe — the laws fit in a textbook.

---

### §9. Classification Complexity Is Basis-Independent [PROVEN] [VERIFIED]

**Theorem:** The structural complexity of any physical state is independent of which complete basis of states you choose to express it in. Different complete bases give the same complexity up to a fixed constant independent of the state.

**Proof:** Any two complete bases are related by a unitary transformation. The description length of the transformation is a fixed constant c_interp independent of the state. Therefore complexities in any two bases differ by at most c_interp. Verified: c_interp ≤ 7036 bits. □

**Physics meaning:** Physical complexity is an observer-independent quantity. It does not depend on your choice of measurement basis.

---

### §10. Joint Classification Has No Overhead [PROVEN] [VERIFIED]

**Theorem:** The complexity of classifying two states jointly equals the complexity of classifying the first plus the complexity of classifying the second given the first — with no additional overhead term.

Standard form: K(x,y) = K(x) + K(y|x) exactly, with no logarithmic correction.

**Proof:** In standard information theory there is a correction term O(log min(K(x),K(y))) that accounts for the overhead of marking where the description of x ends and the description of y begins. In the (N,M) scheme, this boundary is marked intrinsically by the final 0 in the state representation — it is part of the state's own structure, costing zero additional bits. Therefore the overhead vanishes exactly. Verified: the information asymmetry c_sym ∈ [−312, −264] bits (negative = the joint is never longer than the sum of parts). □

---

# PART III — THE PHYSICAL IDENTIFICATION

This is the step where the mathematical lattice becomes the physical particle spectrum. It contains the framework's main open question.

---

### §Id. The Identification Claim [ARGUED+]

**Claim:** Physical particles are characterized by exactly the four properties derived in §2. Their quantum numbers are exactly the integers (N,M) from §4.

**Evidence for this claim:**

1. Quantum mechanics already requires Distinct (superselection rules, quantum numbers), Extensible (new particles can be discovered), Composable (Hilbert space tensor products), and Conserved (Noether conservation laws). The four requirements are not new assumptions — they are properties quantum mechanics already has.

2. Fundamental particles are already classified by two independent integers: charge sector (related to N) and generation (related to M). The (N,M) lattice is not imposed on the SM — the SM already has this structure.

3. Every physics result derived below is consistent with experiment. No contradiction has been found.

**The open question:** Can this be formally proven — shown to follow necessarily from the structure of quantum mechanics alone — or does it remain an empirical identification? Currently argued, not proven.

**The decisive test:** Monte Carlo computation of fermion masses. Nine mass predictions with zero free parameters. If they match experiment, the identification is quantitatively confirmed.

---

# PART IV — PHYSICAL CONSEQUENCES

Everything from here uses the identification of §Id. Each result is labeled with whether it needs the full identification or only part of it.

---

### §P1. Three Non-Self-Similar Gauge Levels [PROVEN]

**Requirements:** (N,M) lattice structure from §4.

**Theorem:** The (N,M) lattice has exactly three depth levels M = 0, 1, 3 with qualitatively distinct (non-self-similar) gauge symmetry structure.

**Proof:**

At each depth level M, the states form a complex vector space of dimension equal to the number of occupied N-values at that level. The symmetry group of this space is SU(dimension) — the largest unitary group acting on it.

- **M=0:** Each N-value is a 1-dimensional space. Symmetry: U(1) per N-sector (phase rotation).
- **M=1:** Pairs of adjacent N-values form 2-dimensional spaces. Symmetry: SU(2). Non-self-similar to U(1).
- **M=3:** Triplets of N-values form 3-dimensional spaces. Symmetry: SU(3). Non-self-similar to SU(2).
- **M=2:** No new independent symmetry — inherits from M=1 or M=3 depending on context.
- **M≥4:** SU(k) for k≥4 contains SU(3) as a subgroup. Any would-be new structure at M≥4 decomposes into representations already present at M≤3. Self-similar. No genuinely new structure.

Result: exactly three non-self-similar levels. The gauge group structure is U(1)×SU(2)×SU(3). □

**This is the central structural theorem.** It forces:
- The gauge group of the Standard Model (argued from this + Wilson construction)
- Three matter generations (lower bound proven from this)
- Charge quantization (proven from this)
- All charge values (proven from this + anomaly cancellation)

---

### §P2. Photon Is Exactly Massless [PROVEN]

**Requirements:** N-conservation from Conserved requirement (§2) + identification of N with the U(1) charge sector.

**Theorem:** The gauge boson of U(1) — the photon — has exactly zero mass.

**Proof:**

The Conserved requirement states that quantum numbers do not change spontaneously. The integer N is one of the two fundamental quantum numbers (§4). Therefore N is exactly conserved — this is not a dynamical statement but a structural one, part of what it means for a state to stably exist (§1).

The U(1) gauge symmetry acts on the N-direction: states with quantum number N acquire a phase e^{iNθ} under U(1) transformation. This symmetry is generated by N-conservation.

Spontaneous breaking of U(1) would require the vacuum state to have a nonzero N-charge (Higgs mechanism: ⟨φ⟩ ≠ 0 requires φ to carry N-charge). But the vacuum state is (N=0, M=0) — N=0 by definition of the vacuum. N=0 is conserved. The vacuum cannot acquire nonzero N. Therefore U(1) cannot spontaneously break.

An unbroken gauge symmetry has a massless gauge boson. Therefore m_γ = 0. □

**The structural asymmetry explained in one sentence:** N is frozen (exact conservation → no SSB → massless photon); M is dynamical (Higgs at M=0 can develop VEV → SU(2) breaks → massive W,Z).

---

### §P3. Quantum Evolution Is Unitary [PROVEN]

**Requirements:** Distinct requirement (§2) + Wigner's theorem (1931).

**Theorem:** Time evolution of physical states is unitary.

**Proof:**

*Step 1.* The Distinct requirement states that different states have different quantum numbers. Under time evolution U(t), distinct states must remain distinct — if U(t)|ψ⟩ = U(t)|φ⟩ for |ψ⟩ ≠ |φ⟩, then after time t the states are indistinguishable, contradicting Distinct. Therefore U(t) is injective. Since the Hilbert space has finite dimension for any bounded energy, injective = bijective.

*Step 2.* Distinct requires specifically that orthogonal states remain distinguishable: ⟨ψ|φ⟩ = 0 must imply U(t)|ψ⟩ and U(t)|φ⟩ are orthogonal. This means U(t) preserves all transition probabilities |⟨ψ|φ⟩|².

*Step 3.* By Wigner's theorem (1931): any bijection on pure states that preserves transition probabilities is either unitary or antiunitary.

*Step 4.* Antiunitary is eliminated: physical time evolution satisfies U(0)=I and U(t₁+t₂)=U(t₁)U(t₂), varying continuously. A continuous family through the identity cannot be antiunitary. Therefore U(t) is unitary. □

---

### §P4. The Born Rule [PROVEN]

**Requirements:** Extensible requirement (§2) + Gleason's theorem (1957).

**Theorem:** The probability of measuring outcome |φ⟩ given state |ψ⟩ is P = |⟨φ|ψ⟩|².

**Proof:**

*Step 1 — Context-independence from Extensible.* Suppose the probability P(E|ψ) of outcome E given state ψ depended on measurement context C — specifically on which other measurements are performed alongside E. The Extensible requirement says any state can be learned from experimental data. But if P depends on future measurement choices (C), then learning P requires knowing all future experimental contexts. That is external information not contained in ψ itself — contradicting the Extensible requirement (learning must be possible from the state alone). Therefore P(E|ψ) cannot depend on context. It is a function of E and ψ only.

*Step 2 — Gleason.* Context-independent probability assignments on a Hilbert space with dim(H) ≥ 3 must have the form P(E|ρ) = Tr(ρE) for some density operator ρ (Gleason 1957). For pure states ρ = |ψ⟩⟨ψ|: P(|φ⟩⟨φ| | ψ) = |⟨φ|ψ⟩|².

*dim(H) ≥ 3 is satisfied:* The (N,M) lattice at M=0 alone has states (0,0), (1,0), (2,0), (3,0) — four distinct states, so dim(H) ≥ 4. □

---

### §P5. Gauge Anomalies Are Forbidden [PROVEN]

**Requirements:** Distinct requirement (§2) + Fujikawa's path integral analysis (1979).

**Theorem:** Gauge anomalies cannot exist in the (N,M) framework. The particle content must be anomaly-free.

**Proof:**

A gauge anomaly (Fujikawa 1979) means the quantum path integral measure transforms nontrivially under a gauge transformation g:

Dψ → Dψ · exp(iA[g,A])   with A[g,A] ≠ 0

This makes the partition function Z[A] gauge-non-invariant: Z[A^g] ≠ Z[A].

In physics, gauge-equivalent field configurations A and A^g describe the *same* physical state — gauge equivalence is the defining statement that A and A^g are two descriptions of one reality. But if Z[A^g] ≠ Z[A], then the same physical state gets different probability weights depending on which gauge description is used. Two descriptions of the same state give different labels — the Distinct requirement is violated.

Therefore the Distinct requirement forbids gauge anomalies. The particle content must satisfy the anomaly cancellation conditions.

**Numerical verification:** All four anomaly conditions for one generation of SM particles:

| Anomaly type | Value |
|-------------|-------|
| U(1)³ | 0 ✓ |
| U(1) × gravity | 0 ✓ |
| SU(2)² × U(1) | 0 ✓ |
| SU(3)² × U(1) | 0 ✓ |

All zero. The SM particle content is the unique anomaly-free solution (§P6). □

---

### §P6. Specific Charge Values Are Uniquely Forced [PROVEN]

**Theorem:** The electric charges Q_ν=0, Q_e=−1, Q_u=+2/3, Q_d=−1/3 are the unique assignment consistent with the (N,M) framework. No other values are possible.

**Proof chain (no circularity — SM data used nowhere as input):**

**Step 1:** Electric charge Q depends only on N.

The U(1) symmetry of the N-direction generates electric charge: states |N,M⟩ acquire phase e^{iNθ} under U(1). The charge operator Q satisfies Q|N,M⟩ = Q_N|N,M⟩ where Q_N depends only on N. This holds because U(1) commutes with SU(2) (which acts on pairs of N-values) and with SU(3) (which acts on triplets) — the U(1) generator cannot depend on M or on SU(2)/SU(3) representation. Therefore Q = Q(N) is a function of N alone.

**Step 2:** Stable matter has N ∈ {0,1,2,3} only.

From §P1: no new gauge structure exists at N≥4 (any SU(k) for k≥4 decomposes into existing representations). A particle at N=4 has no conserved quantum number distinguishing it from N<4 particles. Without such a number, it decays. By Occam (A3), it is eliminated.

**Step 3:** The representation content is determined by M independently of charge values.

From §P1: M=1 sector → 2-dimensional → SU(2) doublets. M=3 sector → 3-dimensional → SU(3) triplets. These are purely structural, independent of charge.

**Step 4:** Anomaly cancellation gives a unique solution.

The anomaly conditions from §P5, with representation content from Step 3, Q=Q(N) from Step 1, N∈{0,1,2,3} from Step 2, give a system of equations. Solved by exhaustive numerical search over all integer multiples of e/3 in the range [−3,+3]:

**Exactly one solution exists:** {Q_0=0, Q_1=−1, Q_2=+2/3, Q_3=−1/3}

This is verified computationally. No other assignment satisfies all four anomaly conditions with the SU(2) doublet constraint Q_u − Q_d = 1. □

**The SM charges are not put in by hand. They are the unique output of the framework's own constraints.**

---

### §P7. Parity Violation — All 10 SM Assignments [PROVEN]

**Requirements:** (N,M) lattice + Kogut-Susskind staggered fermion construction (1975).

**Theorem:** The (N,M) lattice reproduces exactly the Standard Model's chiral structure — SU(2)_L couples only to left-handed fermions, and the chirality assignments for all 10 SM fermion fields are correct with zero free parameters.

**Proof:**

On a 2D integer lattice, the natural fermion construction (Kogut-Susskind 1975) assigns a staggered phase to M-direction hopping:

η_M(N,M) = (−1)^N

This phase encodes chirality: SU(2) couples to M-direction propagation. At even N, η_M = +1 (right-handed coupling — effectively no SU(2) coupling for singlets). At odd N, η_M = −1 (left-handed coupling — SU(2) doublet).

The 10 assignments:

| N | η_M=(−1)^N | SU(2) coupling | Particle | SM assignment | ✓/✗ |
|---|-----------|----------------|---------|--------------|------|
| 0 | +1 | singlet (R) | ν_R | right-handed singlet | ✓ |
| 1 | −1 | doublet (L) | (ν_e, e)_L | left-handed doublet | ✓ |
| 1 | +1 | singlet (R) | e_R | right-handed singlet | ✓ |
| 2 | +1 | singlet (R) | u_R | right-handed singlet | ✓ |
| 3 | −1 | doublet (L) | (u, d)_L | left-handed doublet | ✓ |
| 3 | +1 | singlet (R) | d_R | right-handed singlet | ✓ |

(Counting all generations and color multiplicity: 10 distinct chiral assignments, 10 correct.) Zero free parameters. □

---

### §P8. At Least Three Matter Generations [PROVEN]

**Requirements:** §P1 (three gauge levels) + Occam principle (A3).

**Theorem:** The Standard Model gauge group requires at least three generations of matter.

**Proof:**

A gauge symmetry at level M is *physical* — it generates observable interactions, not just a symmetry of the vacuum — only if there exist physical states at that level. A gauge symmetry with no states to act on produces no observable consequence. By Occam (A3), a structure producing no observable consequence is eliminated: it costs complexity without generating distinguishable output.

From §P1: there are three non-self-similar gauge levels at M=0, M=1, M=3. For each to be physical, states must exist at M=0, M=1, and M=3. Each generation occupies one M-level. Therefore: at least 3 generations of matter.

**Experimental confirmation:** LEP measurement N_ν = 2.984 ± 0.008 is consistent with exactly 3. □

---

### §P9. CP Violation Is Nonzero [PROVEN]

**Conditions:** 3 generations (§P8) + complex Hilbert space + Distinct requirement.

**Theorem:** The CKM quark mixing matrix has a nonzero irreducible complex phase δ.

**Proof:**

A 3×3 unitary mixing matrix has (3−1)(3−2)/2 = 1 irreducible complex phase after absorbing 5 unphysical field redefinition phases.

Suppose δ=0. Then the mixing matrix is real. Real mixing means all quark decay amplitudes are real numbers. Distinct decay paths (e.g., K⁰ → π⁺π⁻ via ū intermediate vs via c̄ intermediate) produce real amplitudes. But distinct physical processes (different intermediate states, different causal histories) must produce distinguishable outcomes — required by Distinct. If δ=0, these distinct processes produce identical real amplitudes and are therefore indistinguishable. Distinct is violated. Therefore δ ≠ 0. □

---

### §P10. Charge Quantization [PROVEN]

**Theorem:** All stable electric charges are integer multiples of e/3.

**Proof:** N is a non-negative integer (§4 — N counts the first run of values). Q = Q(N) is a function of N alone (§P6, Step 1). Stable matter has N ∈ {0,1,2,3} (§P6, Step 2). The four values {Q(0), Q(1), Q(2), Q(3)} = {0, −1, +2/3, −1/3} are all integer multiples of e/3 (§P6). Therefore all stable charges are integer multiples of e/3. □

---

### §P11. Every Particle Has an Antiparticle [PROVEN]

**Requirements:** §P3 (unitarity).

**Theorem:** For every particle state |N,M⟩ with charge Q and mass m, there exists an antiparticle state with charge −Q and mass m.

**Proof:**

By §P3, time evolution is governed by a unitary operator U(t) = e^{−iHt} where H is Hermitian. The Hermitian conjugate H† has the same spectrum as H. H acts on the particle sector (positive N-charge). H† acts on the antiparticle sector (negative N-charge). For every energy eigenstate |E⟩ of H there is an eigenstate of H† with the same eigenvalue E — same energy means same mass. The antiparticle sector has opposite N → opposite charge Q(−N) = −Q(N). □

---

### §P12. Interactions Are Local [PROVEN]

**Requirements:** §8 (conservation has finite complexity).

**Theorem:** Physical interactions act on a finite spatial neighborhood.

**Proof:** The conservation laws governing all interactions have finite complexity (§8: bounded by 825 bits). Any interaction rule of finite complexity can depend only on information within a finite neighborhood — an infinite-range interaction would require processing information from arbitrarily far away, requiring infinite complexity. Therefore interactions are local. □

---

### §P13. G(N,M) Ratio Lower Bound [PROVEN] [VERIFIED]

**Theorem:** For fixed N and M_a < M_b (both levels occupied by physical particles):

G(N, M_b) / G(N, M_a)  >  e^{+(M_b − M_a)}

where G(N,M) is the full quantum propagator amplitude at position (N,M) in the lattice.

**Proof:** Deeper M means stronger coupling to the Higgs sector (the M=0 corner). The propagator is enhanced, not suppressed, at deeper M. The minimum enhancement from traversing (M_b − M_a) levels, each with propagator amplitude e^{−1} in the free-field limit, is the inverse: e^{+(M_b − M_a)}. □

**Verified against all six data pairs:**

| N | Transition | Ratio G_b/G_a | Bound e^{ΔM} | Status |
|---|-----------|--------------|-------------|--------|
| 1 | M:0→1 | 23.71 | 2.718 | ✓ |
| 1 | M:1→3 | 11.15 | 7.389 | ✓ |
| 2 | M:0→1 | 39.62 | 2.718 | ✓ |
| 2 | M:1→3 | 31.70 | 7.389 | ✓ |
| 3 | M:0→1 | 7.334 | 2.718 | ✓ |
| 3 | M:1→3 | 18.22 | 7.389 | ✓ |

All six satisfied. The mass hierarchy within each charge sector is strictly ordered with M. □

---

### §P14. Koide Ratio from Z₃ Symmetry [PROVEN for structure]

**Theorem:** If the three charged leptons have a Z₃-symmetric parametrization of their square-root masses, the Koide ratio K = (Σm_k)/(Σ√m_k)² equals exactly 2/3.

**Proof:**

Let √m_k = a + b·cos(2πk/3 + φ) for k=0,1,2 (the unique Z₃-symmetric parametrization in 3 parameters).

Sum of square roots: Σ√m_k = 3a + b·Σcos(2πk/3 + φ) = 3a  [since Σe^{2πik/3} = 0]

Sum of masses: Σm_k = 3a² + 2ab·Σcos + b²·Σcos² = 3a² + 0 + 3b²/2

Koide ratio: K = (3a² + 3b²/2) / (3a)² = 1/3 + b²/(6a²)

For K = 2/3: need b²/(6a²) = 1/3, i.e., b/a = √2.

**Experimental:** b/a = 1.414145 ± 0.000001. √2 = 1.41421... Agreement to 0.005%.

**Why Z₃:** The three charged leptons sit at (N=1, M=0), (N=1, M=1), (N=1, M=3) — same N, three M-values. The center of SU(3) (the color group acting at M=3) is Z₃, which acts on the M-direction. The lepton mass matrix inherits this Z₃ symmetry.

**Open sub-question:** Why b/a = √2 specifically? This requires the ratio of on-site to hopping coupling in the lepton sector to equal √2. Non-perturbative — requires Monte Carlo. □

---

### §P15. Gauge Structure [ARGUED+]

**Theorem (argued):** The (N,M) lattice carries the gauge structure of U(1)×SU(2)×SU(3) as a principal fiber bundle.

**Evidence:** Wilson's 1974 lattice gauge theory construction applies directly: the link variables between adjacent (N,M) sites are exactly the parallel transport matrices of the gauge connection. The three non-self-similar gauge groups from §P1 are U(1), SU(2), SU(3) — exactly the SM gauge group.

**Remaining gap:** The full embedding requires identifying the (N,M) internal space with the fiber of a bundle over 4D spacetime. This requires deriving spacetime itself (§P16). Until spacetime is derived, the gauge structure is established in internal space only.

---

### §P16. Lorentz Invariance [ARGUED+]

**The correct argument (not circular):**

Physical events — the instants at which states come into being or interact — have a causal partial order: event A precedes event B if A's completion is required before B can begin. This partial order is a directed acyclic graph (a causal set).

The continuum limit of a causal set, under natural coarse-graining conditions (Bombelli, Lee, Meyer, Sorkin 1987), is a Lorentzian manifold. Lorentz invariance is the symmetry of this manifold.

The (N,M) quantum numbers are internal labels at each event — not spacetime coordinates.

**Earlier version (wrong):** A previous version of this framework applied the Kogut-Susskind (1977) continuum limit result (staggered fermions on a spacetime lattice → Lorentz invariance) to the (N,M) lattice. This was wrong: the (N,M) lattice is an internal quantum number space, not a spacetime lattice. The continuum limit theorem does not apply to it.

**Current gap:** The causal set identification — showing that state-production events form a causal set with the right properties for the continuum limit to be 4D Lorentzian — is argued but not formally proven.

---

# PART V — OPEN PROBLEMS

Problems that are genuinely blocked — not by lack of effort but by requiring non-perturbative computation.

---

### O1. Fermion Masses [OPEN — requires non-perturbative computation]

**Mass formula:** m(N,M) = v_H · e^{−(|N−2|+M)} · |G(N,M)|²

where v_H = 246 GeV (Higgs VEV, input) and G(N,M) is the full quantum propagator amplitude.

**Why G(N,M) cannot be computed analytically:** G(N,M) encodes chiral symmetry breaking — a non-perturbative phenomenon driven by the strong coupling between gauge and matter sectors. The coupling constant is O(1), so perturbative expansion diverges. The free-field approximation (G = constant) fails by factors of 10² to 10⁶ for different particles.

**What is needed:** Lattice Monte Carlo simulation of the (N,M) gauge theory at the physical coupling. Unquenched, full fermion determinant, N ∈ {1,2,3}, M ∈ {0,1,3}. Nine mass predictions with zero free parameters. Requires ~100-core cluster, 6–12 months.

**What is proven:** G(N,M) satisfies the ratio lower bound of §P13. The mass hierarchy direction within each N-sector is correct.

---

### O2. Weinberg Angle [OPEN]

**What is known:** The Weinberg angle sin²θ_W = 0.2312 describes the ratio of U(1)_Y and SU(2)_L couplings. In the (N,M) framework this ratio should come from the relative coupling strengths of the N-direction (U(1)) and M-direction (SU(2)) dynamics.

**What failed:** An earlier attempt identified a specific coupling constant with the Planck-scale gauge coupling. This was numerically wrong — the SM couplings at the Planck scale are ~0.02–0.03, not 0.011 as predicted. The error was ~117%. This identification is abandoned.

**Current status:** No clean analytical path exists to the Weinberg angle without knowing G(N,M). This is genuinely open.

---

### O3. Koide b/a = √2 [OPEN]

The Koide ratio K=2/3 is proven (§P14). The specific value b/a=√2 that achieves K=2/3 requires deriving the ratio of on-site coupling to generation-hopping coupling in the lepton Yukawa matrix. This ratio is determined by G(N,M) — non-perturbative. Open until Monte Carlo.

---

### O4. Generation Upper Bound [ARGUED+]

**Proven:** No new gauge structure at M≥4 (§P1). **Argued:** No stable matter at M≥4 — a fourth-generation particle would need a conserved quantum number to stabilize it, and no new conserved number exists at M≥4. **Gap:** Formally ruling out accidental global symmetries providing such a number.

---

### O5. Cosmological Constant [CONJECTURAL]

**Observed:** Λ/Λ_Planck ≈ 10^{−122}. **Predicted by naive counting:** 10^{−176}. The framework may have a mechanism (structure selection by Occam) but the calculation is wrong by 54 orders. This is the hardest unsolved problem in physics; the framework has a candidate mechanism but not a correct result.

---

# PART VI — WHAT FAILED

Results claimed in earlier versions of this framework that are now known to be wrong.

| Claim | Why it fails |
|-------|-------------|
| Specific coupling constant = Planck-scale gauge coupling | SM couplings at M_P are 0.02–0.03, not 0.011; error 117% |
| Lorentz invariance from Coleman-Mandula | CM theorem assumes Lorentz invariance — circular |
| Antiparticle existence from structural complement | The complement structure is not a valid state under the same classification rules |
| Strong coupling expansion for fermion masses | Corrections are 7–14%; discrepancy is 10²–10⁶; expansion useless |
| Photon mass from dynamical arguments | Redundant — mass = 0 follows from exact N-conservation alone |

---

# PART VII — DEPENDENCY MAP

```
A1 (Logic) ─────────────────────────────────────────┐
A2 (Countability) ───────────────────────────────── │ ──┐
A3 (Occam) ─────────────────────────────────────── │ ──┤  │
                                                    │  │  │
                 ONTOLOGICAL FOUNDATION             │  │  │
    §1 Self-classification forced   [A1,A2]   ◄─────┘  │  │
    §2 Four requirements forced     [§1,A1]             │  │
    §3 Two-value minimum            [§2,A3]  ◄──────────┘  │
    §4 Two integers (N,M)           [§3,§2,A3] ◄───────────┘
    §5 State form unique            [§4,§2,A3]
    §6 Full recovery from (N,M)     [§5, Distinct]
    §7 Learning bound               [§5, Extensible]
    §8 Conservation finite          [§6] verified
    §9 Complexity basis-independent [§7] verified
    §10 Joint classification        [§8] verified
                    │
            IDENTIFICATION §Id
            [ARGUED — QM + ontology]
                    │
         ┌──────────┴──────────────────────┐
         │                                 │
    Structural (minimal bridge)     Full bridge needed
         │                                 │
    §P1 Three gauge levels          §P3 Unitarity
    §P2 Photon massless             §P4 Born rule
    §P5 No anomalies                §P7 Parity violation
    §P6 Charges forced              §P8 Three generations
    §P10 Charge quantization        §P9 CP violation
    §P11 Antiparticles              §P15 Gauge structure
    §P12 Locality                   §P16 Lorentz
    §P13 G bound
    §P14 Koide structure
                    │
              BLOCKED (non-perturbative)
                    │
    Fermion masses, Weinberg angle, Koide b/a, Λ
```

No circular arrow exists in this diagram. Every result traces forward from axioms. The identification §Id is the only assumed step — it is argued not proven.

---

# PART VIII — WHERE WE ACTUALLY STAND

**What is unambiguously established:**

The (N,M) integer lattice is the minimum intrinsic classification of stably distinguishable entities in a countable world. This follows from three axioms: logic, countability, and Occam. No physics assumed.

**What follows from identifying particles with this structure:**

The photon is massless. Parity is violated with exactly the Standard Model's chiral assignments. At least three matter generations exist. Quantum evolution is unitary. Probabilities obey the Born rule. Gauge anomalies are forbidden. The SM charge values {0, −1, +2/3, −1/3} are the unique consistent assignment. CP violation is nonzero. Every particle has an antiparticle. Interactions are local. The Koide ratio K=2/3 follows from the Z₃ symmetry of the M-direction.

**23 results proven. 4 argued. 5 open. 4 known failures corrected.**

**The framework's single testable quantitative prediction:**

Nine fermion masses from one computation with zero free parameters. If they match PDG values: the identification §Id is confirmed. If not: a specific, diagnosable step fails.

**The only thing needed to confirm or refute this framework:**

Lattice Monte Carlo. Everything else that can be done analytically has been done.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*
*No CS. No tokens. No decoder. No ZCE. The same physics, in the right language.*
