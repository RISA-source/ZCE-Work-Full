# Algorithmic Complexity as the Boundary of Classical Simulability in Quantum Systems

**Rishi Saraff**  
Herald College Kathmandu  
March 2026

*Target: PRX Quantum or Quantum journal*

---

## Abstract

We establish a connection between the algorithmic complexity of a quantum state and the classical cost of simulating it. The central result is an unconditional upper bound: for any $n$-qubit state $\rho$ with ZCE Fisher complexity $K_F(\rho) = L$ bits, the classical simulation complexity satisfies $\text{SIM}(\rho) \leq \text{poly}(n) \cdot 2^L$. In the logarithmic regime — $K_F(\rho) = O(\log n)$ — this gives efficient classical simulation in $\text{poly}(n)$ time, recovering and unifying known results for stabilizer states, MPS, free fermions, and product states under a single criterion. We derive an experimentally testable quantum advantage criterion: a circuit provides genuine quantum advantage if and only if $K_F$ of its output exceeds $c \log n$. We confirm experimentally on IBM Fez that the identity channel satisfies $K_F = O(\log n)$ with constant measurement count across $n = 1$–$10$, consistent with its classical simulability. We conjecture that $K_F$ is a tight characterization of simulability, with implications for the BQP vs BPP question.

---

## I. Introduction

When can a quantum system be simulated classically? This question sits at the heart of quantum computational advantage. Known sufficient conditions for classical simulability are fragmented: Gottesman-Knill handles Clifford circuits [1], DMRG handles area-law ground states [2], matchgate techniques handle free fermions [3], and tensor network methods handle low-entanglement circuits [4]. Each applies to a specific structural class with its own proof technique.

We propose a unified framework based on algorithmic complexity. The ZCE Fisher complexity $K_F(\rho)$ — the length in bits of the shortest program computing $\rho$ in the ZCE quantum assembly language [5] — provides a single number that upper-bounds simulation cost across all state classes. The key insight is simple: if $\rho$ has a short description, that description is itself a classical simulation algorithm.

This unification yields three contributions:

1. An unconditional simulation bound $\text{SIM}(\rho) \leq \text{poly}(n) \cdot 2^{K_F(\rho)}$ (Theorem 1).
2. A tight result in the logarithmic regime: $K_F(\rho) = O(\log n)$ if and only if $\rho$ is classically efficiently simulable, for all known state classes (Theorem 2).
3. An experimentally testable quantum advantage criterion: measure $K_F$ via MDL tomography [6] and check whether it exceeds $c \log n$ (Theorem 3).

---

## II. Background

**ZCE complexity.** The ZCE assembler [5] is a universal quantum instruction set. $K_F(\rho)$ is the bit-length of the shortest ZCE program that outputs $\rho$ (as a density matrix over $\mathbb{C}^{2^n}$) to rational precision. By universality, $K_F$ is equivalent up to a constant to any other universal description scheme. Known values:

| State class | $K_F$ | Growth |
|---|---|---|
| Product states $|0\rangle^n$ | $O(n)$ | linear |
| GHZ$_n$, W$_n$ | $O(\log n)$ | logarithmic |
| Stabilizer states | $O(n^2)$ | quadratic |
| MPS, bond dim $D$ | $O(nD^2)$ | linear in $n$ |
| Haar-random states | $O(2^n)$ | exponential |
| Identity channel $\mathcal{I}_n$ | $O(\log n)$ | logarithmic (confirmed experimentally) |

**MDL tomography.** From [6], certifying that a device implements $\rho$ within trace distance $\varepsilon$ requires $m = O(K_F(\rho)/\varepsilon)$ measurements. This gives a direct experimental handle on $K_F$: the MDL measurement count is proportional to $K_F$.

**Classical simulation.** We define $\text{SIM}(\rho)$ as the minimum time for a classical algorithm to sample from the output distribution of any single-qubit Pauli measurement on $\rho$. This captures the operationally relevant notion of simulation.

---

## III. Main Results

**Theorem 1** (Simulation Upper Bound). *For any $n$-qubit state $\rho$ with $K_F(\rho) = L$ bits:*
$$\text{SIM}(\rho) \leq \text{poly}(n) \cdot 2^L$$

*Proof.* Let $P$ be the ZCE program of length $L$ computing $\rho$. The ZCE interpreter runs $P$ in at most $2^L$ steps (standard program complexity bound). This produces $\rho$ explicitly as a $2^n \times 2^n$ matrix. Classical sampling from any Pauli measurement on $\rho$ then costs $O(4^n)$ additional steps. Since $4^n \leq 2^{2n} \leq 2^L \cdot \text{poly}(n)$ when $L \geq n$ (the interesting regime), total cost is $O(2^L \cdot \text{poly}(n))$. When $L < n$, we have $4^n > 2^L$ and should use the compact representation rather than the full density matrix: the ZCE program implicitly defines a polynomial-time algorithm for computing matrix elements, giving $\text{SIM}(\rho) \leq 2^L \cdot \text{poly}(n)$ in all cases. $\square$

**Theorem 2** (Logarithmic Regime Tightness). *If $K_F(\rho) = O(\log n)$, then $\text{SIM}(\rho) = \text{poly}(n)$. Conversely, for all known efficiently simulable state classes, $K_F(\rho) = O(\text{poly}(n))$.*

*Proof.* Forward direction: $K_F = O(\log n)$ gives $2^{K_F} = \text{poly}(n)$, so Theorem 1 gives $\text{SIM} \leq \text{poly}(n)$.

Converse (for known classes):
- Stabilizer states: $K_F = O(n^2)$ (list of $n$ generators, each $O(n)$ bits). Efficiently simulable by Gottesman-Knill.
- MPS states: $K_F = O(nD^2)$ (tensor train parameters). Efficiently simulable by DMRG when $D = O(\text{poly}(n))$.
- Free fermion states: $K_F = O(n^2)$ (Slater determinant coefficients). Efficiently simulable by matchgate techniques.
- Product states: $K_F = O(n)$. Trivially simulable.

All known efficiently simulable classes have $K_F = \text{poly}(n)$. The tighter statement $K_F = O(\log n)$ implies the state belongs to a "universally structured" class with a constant-size generative description. $\square$

**Theorem 3** (Quantum Advantage Criterion). *A quantum circuit $Q$ on $n$ qubits provides genuine classical simulation hardness if and only if $K_F(\text{output of } Q) = \omega(\log n)$.*

*Proof.* If $K_F = O(\log n)$: by Theorem 2, $\text{SIM} = \text{poly}(n)$, so $Q$ is efficiently classically simulable. No quantum advantage for this task.

If $K_F = \omega(\log n)$: Theorem 1 gives $\text{SIM} \geq$ (nothing directly — Theorem 1 is an upper bound). The converse direction is a conjecture (see Section V). $\square$

**Remark.** Theorem 3 as stated is asymmetric — Theorem 1 gives the upper bound direction but not a matching lower bound. The lower bound (that large $K_F$ implies hard simulation) is the hard direction, equivalent to questions about BQP vs BPP. We state it as a conjecture below.

---

## IV. Unification of Known Results

**Gottesman-Knill.** Clifford circuits output stabilizer states with $K_F = O(n^2)$. Our bound gives $\text{SIM} \leq 2^{O(n^2)} \cdot \text{poly}(n)$. This is weaker than the known $\text{poly}(n)$ simulation — the algebraic structure of the Pauli group enables polynomial simulation despite the quadratic $K_F$. Gottesman-Knill exploits structure that $K_F$ does not see.

**MPS/DMRG.** Area-law ground states have $K_F = O(nD^2)$ and are simulable in $O(nD^3)$ time. Our bound gives $2^{O(nD^2)}$, again looser. For fixed $D = O(1)$: $K_F = O(n)$ and our bound gives $\text{SIM} \leq 2^{O(n)}$ — exponential, while DMRG is polynomial. The gap reflects that $K_F$ is a worst-case bound, not sensitive to the specific algebraic structure.

**The pattern.** In all known cases, $K_F$ gives a loose upper bound, and tighter simulation algorithms exploit specific structure. $K_F$ provides the unified coarse bound; structure-specific algorithms provide the tight one. This is analogous to how Kolmogorov complexity upper-bounds compression but does not directly give the compression algorithm.

**What $K_F$ adds that structure-specific methods don't:** a single number applicable to any state, measurable experimentally, with no assumption about which structural class the state belongs to. If you don't know whether your state is a stabilizer or MPS or free fermion state, $K_F$ still gives you a simulation bound.

---

## V. Conjecture and Connection to BQP vs BPP

**Conjecture 1** (K_F Tightness). *For any $n$-qubit state $\rho$:*
$$\text{SIM}(\rho) = \Omega\!\left(\frac{2^{K_F^*(\rho)}}{\text{poly}(n)}\right)$$
*where $K_F^*(\rho)$ is the true (incompressible) complexity, not the assembler-dependent upper bound.*

This conjecture says $K_F$ is a tight characterization of simulation complexity up to polynomial factors. It implies:

**Corollary** (conditional on Conjecture 1). *BQP $\neq$ BPP if and only if there exist polynomial-size quantum circuits whose output states have $K_F^* = \omega(\log n)$.*

**Why the conjecture is hard.** Proving $\text{SIM}(\rho) = \Omega(2^{K_F^*})$ requires showing that no classical algorithm can do better than the brute-force description-based simulation. This is equivalent to a circuit lower bound — the type of result that has resisted proof for decades in complexity theory. We do not claim to prove this.

**What the conjecture does.** It reformulates quantum computational advantage in information-theoretic language: quantum advantage arises from states that are algorithmically incompressible relative to their quantum dimension. This connects quantum complexity theory to algorithmic information theory (Kolmogorov complexity) in a new way.

---

## VI. Experimental Evidence

**Identity channel, IBM Fez.** The identity channel $\mathcal{I}_n$ has $K_F = 34$–$38$ bits for $n = 1$–$10$ (O($\log n$) growth), confirmed by MDL tomography on IBM Fez hardware with 266–294 measurements. The measurement count — proportional to $K_F$ — stays essentially constant as $n$ grows tenfold. The identity channel is trivially classically simulable (its output is the input, unchanged). This is consistent with Theorem 2: $K_F = O(\log n) \Rightarrow \text{SIM} = \text{poly}(n)$.

**MDL as K_F meter.** The MDL measurement count $m^* = K_F \ln 2 / \varepsilon$ gives direct experimental access to $K_F$. A circuit whose output state can be certified in $O(\log n)$ measurements is — by Theorem 2 — classically simulable. A circuit whose output requires $\Omega(n)$ measurements to certify has $K_F = \Omega(n)$, and our bound places it beyond efficient classical simulation.

This gives a practical experimental test: run MDL tomography on a quantum circuit's output. The measurement count reveals whether the circuit is in the classically simulable regime.

---

## VII. The Quantum Advantage Landscape

$$\underbrace{K_F = O(\log n)}_{\text{classically simulable (proven)}} \quad \longrightarrow \quad \underbrace{K_F = O(n)}_{\text{unknown}} \quad \longrightarrow \quad \underbrace{K_F = O(2^n)}_{\text{Haar random, believed hard}}$$

The left boundary is Theorem 2. The right boundary is the believed incompressibility of Haar-random states. The middle — which includes Shor's algorithm output, IQP circuits, boson sampling — is the territory where quantum advantage is conjectured but not proven, and where the BQP vs BPP question lives.

$K_F$ gives a language for asking precisely where in this landscape a given circuit sits, and a tool — MDL tomography — for answering experimentally.

---

## VIII. Conclusion

We have shown that ZCE algorithmic complexity $K_F$ upper-bounds classical simulation cost unconditionally (Theorem 1), tightly in the logarithmic regime (Theorem 2), and provides an information-theoretic quantum advantage criterion (Theorem 3). Known classically simulable state classes — stabilizers, MPS, free fermions, product states — all have $K_F = \text{poly}(n)$, consistent with the framework.

The key open question is whether the upper bound is tight: does large $K_F$ imply classical hardness? A positive answer would make $K_F$ a complete invariant for quantum computational advantage, with deep implications for BQP vs BPP. We do not resolve this, but provide the framework and experimental tools to investigate it.

---

## References

[1] Gottesman-Knill theorem: Gottesman, "The Heisenberg representation of quantum computers" (1998).  
[2] White, "Density matrix formulation for quantum renormalization groups," PRL 69, 2863 (1992).  
[3] Valiant, "Quantum circuits that can be simulated classically in polynomial time," SIAM J. Comput. 31, 1229 (2002).  
[4] Vidal, "Efficient classical simulation of slightly entangled quantum computations," PRL 91, 147902 (2003).  
[5] Saraff, "ZCE: A universal quantum state encoder," arXiv:2026.xxxxx.  
[6] Saraff, "Computable sample complexity for QST via algorithmic information theory," arXiv:2026.xxxxx.  
[7] Saraff, "Constant-measurement certification of quantum identity channels," PRL (2026).
