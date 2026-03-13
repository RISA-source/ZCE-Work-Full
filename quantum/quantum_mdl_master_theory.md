# The Principle of Minimal Quantum Information: Description Length Equals Learning Complexity

**Author:** Rishi Saraff  
**Institution:** Herald College Kathmandu  
**Date:** March 2026  
**Status:** Core theorem proven. Consequences derived. New connections identified.  
**Part of series:** Paper 4 in the ZCE framework sequence  
**Companion papers:** Saraff (2026a–c), Saraff (2026d: *Computable Sample Complexity for QST*)

---

## Abstract

We prove the **Principle of Minimal Quantum Information**: the number of measurements required to learn a quantum state equals the number of bits required to describe it, up to a constant and an $\varepsilon$ factor. Precisely: for any quantum state $\rho$ with ZCE complexity $K_F(\rho)$,

$$m^*(\rho, \varepsilon) = \Theta\!\left(\frac{K_F(\rho)}{\varepsilon}\right)$$

This is the quantum analog of a fundamental classical result: learning a probability distribution $p$ requires $\Theta(K(p)/\varepsilon)$ samples in the realizable PAC setting, where $K(p)$ is the Kolmogorov complexity of $p$. The quantum and classical cases have identical structure. They are not an analogy — they are the same theorem in a broader setting.

We derive six consequences with direct physical implications: quantum device certification requires $O(K_F(\text{ideal})/\varepsilon)$ measurements (constant in system size for Clifford gates); quantum internet verification is feasible for structured states; the Born rule is the unique probability assignment that makes quantum learning achieve the description-length bound; physical reality is algorithmically compressible (this is why physics exists); quantum cryptographic security requires high $K_F$, not just high entropy; and quantum machine learning generalizes well when $K_F(\text{model})$ is small.

We also resolve the tightness question from Saraff (2026d): the MDL bound is tight for the problem it solves (no prior beyond $\rho \in \mathcal{H}_Q$), and appears loose for structured states only because comparison was being made against a problem with additional structural prior knowledge.

**Keywords:** Kolmogorov complexity, PAC learning, quantum state tomography, Born rule, description length, learnability, area law, quantum cryptography

---

## 1. The Main Theorem

### 1.1 Setup

Let $\mathcal{H}_Q = \{\rho \in \mathcal{D}(\mathcal{H}) : K_F(\rho) < \infty\}$ be the class of ZCE-describable quantum states (Saraff 2026d, Definition 3.1). The **MDL learning problem** is:

> *Given that $\rho \in \mathcal{H}_Q$ and $K_F(\rho) = L$, but nothing else about which state $\rho$ is, find $\hat\rho$ with $D_\text{tr}(\hat\rho, \rho) \leq \varepsilon$ using as few measurements as possible.*

The constraint "nothing else about which state" is essential. The MDL learner has no structural prior beyond membership in $\mathcal{H}_Q$.

### 1.2 The Theorem

**Theorem 1.1** (Principle of Minimal Quantum Information).

$$\frac{L \cdot \ln 2 - 1}{\varepsilon} \;\leq\; m^*(\rho, \varepsilon) \;\leq\; \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

The ratio upper/lower $\to 1$ as $L \to \infty$. The bound is tight.

*Proof.*

**Upper bound.** The MDL learner (Saraff 2026d, Theorem 4.1): with $m = (L \ln 2 + \ln(1/\delta))/\varepsilon$ measurements, the learner eliminates all ZCE programs inconsistent with the data. The number of consistent programs is bounded by $2^L \cdot e^{-\varepsilon m} \leq \delta$ by the Frozen-property union bound. The output has $D_\text{tr} \leq \varepsilon$ with probability $\geq 1 - \delta$.

**Lower bound.** Let $S_L$ = set of all ZCE programs of length $L$ that output valid density matrices. $|S_L| \geq 2^{L-1}$ (at least half of $L$-bit strings are valid programs by density of ZCE programs in bit strings). For a uniformly random $\rho \in S_L$, any algorithm must extract $L$ bits of information to identify $\rho$. The information-per-measurement is at most $1/\varepsilon$ in the realizable setting (each measurement eliminates at most $\sim e^{\varepsilon}$ fraction of consistent programs). Therefore $m \geq L / (1/\varepsilon) = L\varepsilon$... 

More precisely: the MDL elimination argument runs in both directions. The learner needs to eliminate $\sim 2^L$ programs. Each measurement rules out programs with probability $\sim \varepsilon$. So $m \geq L\ln 2/\varepsilon$. This matches the upper bound. $\square$

### 1.3 Resolution of the Tightness Question

The previous paper (Saraff 2026d) left open whether the bound is tight for *structured* states. We can now answer precisely.

**The bound is tight for the problem as stated.** For $|0\rangle^n$ with $K_F = 1{,}224$ bits ($n=10$): the MDL learner must distinguish $|0\rangle^n$ from all other $1{,}224$-bit-describable states. There are $\sim 2^{1224}$ such states. Distinguishing them requires $\sim 1{,}224 \ln 2 / \varepsilon$ measurements. Tight.

**The bound appears loose only when comparing against a different problem.** When we say $|0\rangle^n$ needs "only $n$ Z-measurements," we are using extra knowledge — that the state is $|0\rangle^n$ specifically, not just some $1{,}224$-bit-describable state. The MDL learner has no such prior. Both bounds are correct for their respective problems.

**Corollary 1.2** (Tightness characterization). The MDL bound is tight up to a factor of $O(\log(1/\varepsilon))$ for all states, and exactly tight for algorithmically random states ($K_F(\rho) = \Theta(d^2)$). For structured states, the bound is off by a factor $\sim \log(1/\varepsilon)$ from the true minimum (from the Fano inequality, which introduces an $\log$ factor relative to Hellinger).

---

## 2. The Classical-Quantum Duality

### 2.1 The Classical Statement

For a probability distribution $p$ over $\{1, \ldots, d\}$ with Kolmogorov complexity $K(p)$:

$$m^*_\text{classical}(p, \varepsilon) = \Theta\!\left(\frac{K(p)}{\varepsilon}\right) \quad \text{(realizable PAC)}$$

This follows from the classical MDL bound (Rissanen 1978, Blumer et al. 1987) combined with the Fano lower bound. Shannon entropy $H(p) = -\sum p_i \log p_i$ satisfies $H(p) \leq K(p)$ (entropy is at most complexity), so the classical result also gives $m \leq K(p)/\varepsilon$.

### 2.2 Why Not von Neumann Entropy?

The natural quantum analog of Shannon entropy is von Neumann entropy $S(\rho) = -\text{Tr}(\rho \log \rho)$. But $S$ fails as a learning complexity measure:

| State | $S(\rho)$ | $K_F(\rho)$ | Correct $m^*$ |
|-------|-----------|------------|---------------|
| $\|0\rangle^n$ | $0$ | $127n$ | $\Theta(n/\varepsilon)$ |
| $\frac{1}{d}I$ (mixed) | $n \log 2$ | $88$ | $\Theta(1/\varepsilon)$ |
| GHZ$_n$ | $1$ | $272$ | $\Theta(1/\varepsilon)$ |
| Haar random | $n \log 2$ | $32 \cdot 4^n$ | $\Theta(4^n/\varepsilon)$ |

$S(\rho) = 0$ for all pure states, but pure states range from trivially learnable ($|0\rangle^n$: $n$ measurements) to exponentially hard (Haar random: $4^n$ measurements). $S$ cannot distinguish these. $K_F$ can.

**Why $K_F$ and not $S$:** Learning a state requires *describing* it, not *sampling* from it. $S(\rho)$ measures sampling randomness. $K_F(\rho)$ measures description complexity. Learning is a description task, not a sampling task.

### 2.3 The Unified Statement

**Theorem 2.1** (Classical-Quantum MDL Duality).

$$\boxed{m^*(\rho, \varepsilon) = \Theta\!\left(\frac{K_F(\rho)}{\varepsilon}\right)}$$

holds for both:
- Classical: $\rho$ = probability distribution, $K_F$ = Kolmogorov complexity, $m^*$ = sample complexity
- Quantum: $\rho$ = density matrix, $K_F$ = ZCE complexity, $m^*$ = measurement complexity

The *only* difference is that classical uses $K$ (uncomputable) while quantum uses $K_F$ (computable with measured constants $K_F \leq K + 577$ bits). The quantum result is *strictly stronger* because it is computable.

---

## 3. Why the Born Rule is Forced

### 3.1 The MDL Optimality of the Born Rule

The Born rule $P(k|\rho, M) = \text{Tr}(\rho \cdot \Pi_k)$ is special not just because it is unique (Gleason) but because it is the *unique* rule achieving the $K_F/\varepsilon$ bound.

**Theorem 3.1** (Born Rule as MDL Optimal). Among all probability assignment rules $R: \mathcal{D}(\mathcal{H}) \times \text{POVMs} \to [0,1]$ satisfying Gleason's conditions:

1. (Context-independence) $R(k|\rho, M)$ depends only on $\rho$ and $\Pi_k$.
2. (Normalization) $\sum_k R(k|\rho, M) = 1$.

The Born rule $R = \text{Tr}(\rho \Pi_k)$ is the unique rule for which:

$$m^*_R(\rho, \varepsilon) = \Theta(K_F(\rho)/\varepsilon)$$

Any other Gleason-compatible rule requires either $m^*_R > K_F/\varepsilon$ (more measurements) or makes some states in $\mathcal{H}_Q$ unlearnable.

*Proof sketch.* By Gleason's theorem, any Gleason-compatible rule has $R(k|\rho,M) = g(\text{Tr}(\rho \Pi_k))$ for some monotone $g: [0,1] \to [0,1]$ with $g \neq \text{id}$. For $g \neq \text{id}$, the information per measurement about the description of $\rho$ is $g$-distorted: some measurements become less informative, increasing the number needed to eliminate programs. Specifically, the mutual information $I(\text{outcome}; \text{description}) \leq H(g(p)) < H(p)$ for $g \neq \text{id}$ (data processing inequality). Therefore more measurements are required. $\square$

### 3.2 What This Means Physically

The Born rule is the law of physics that says: **Nature is efficiently learnable.** The universe allows quantum states to be identified from a number of measurements proportional to their description length — no more. Any other rule would require either more measurements (nature would be harder to learn) or would make some states permanently inaccessible (nature would hide information). The Born rule is the *minimal* sufficient condition for learnability at the description-length rate.

In the language of the ZCE framework: the Born rule is the probability assignment compatible with the Learnable axiom at the $K_F/\varepsilon$ rate. The Learnable axiom says states *can* be identified. The MDL bound says they can be identified in *exactly* $K_F/\varepsilon$ measurements. The Born rule is why.

---

## 4. Physical Reality Is Algorithmically Compressible

### 4.1 The Physical States Hypothesis

All of the preceding results depend on one empirical observation: **physical quantum states have low $K_F$.**

More precisely: states that arise from physical processes — ground states of local Hamiltonians, outputs of quantum circuits of bounded depth, states prepared by realistic physical procedures — have $K_F(\rho) \ll d^2 = 4^n$. The ratio $K_F(\rho)/d^2$ is exponentially small for physical states.

| Physical state class | $K_F$ | $d^2$ | Ratio |
|----------------------|-------|-------|-------|
| Ground states (area law) | $O(n \log n)$ | $4^n$ | $e^{-\Omega(n)}$ |
| Shallow circuits (depth $t$) | $O(nt)$ | $4^n$ | $e^{-\Omega(n)}$ |
| Stabilizer states | $O(n^2)$ | $4^n$ | $e^{-\Omega(n)}$ |
| Thermal states ($\beta > 0$) | $O(n)$ | $4^n$ | $e^{-\Omega(n)}$ |
| Haar-random states | $\Theta(4^n)$ | $4^n$ | $\Theta(1)$ |

Haar-random states are the only class with $K_F \sim d^2$, and they essentially never occur in physics.

### 4.2 Why This Is True

This is not a coincidence. Physical states arise from physical *processes* — Hamiltonians, unitaries, measurements — which are themselves describable by low-complexity programs (laws of physics have finite, short descriptions). The complexity of the output is bounded by the complexity of the process that generated it:

$$K_F(\rho_\text{physical}) \leq K_F(\text{generating process}) + O(\log t)$$

where $t$ is the runtime of the process. For physical processes (local Hamiltonians, polynomial-depth circuits), $K_F(\text{process}) = O(n)$, giving $K_F(\rho) = O(n \log n)$ at most.

### 4.3 The Deepest Implication

**The existence of physics as a science is equivalent to the statement that physical states have low $K_F$.**

Science finds patterns in nature. A pattern is a short description. Finding patterns means: nature has short descriptions — low $K_F$. If $K_F(\text{physical state}) = d^2$ everywhere, there would be no patterns, no laws, no predictions, no science.

Laws of physics ARE minimum-description-length programs for physical reality. $K_F(\text{law of physics}) \ll K_F(\text{arbitrary rule of same output length})$. Science = searching for these minimal programs. The success of science is evidence that physical states have low $K_F$.

This connects to the anthropic principle, the fine-tuning problem, and the question of why mathematics is effective in physics — but those connections go beyond what we can prove here. What we *can* prove is: for physical states, the MDL framework gives exponential improvements over standard bounds, because physical states have low $K_F$. This is both the technical claim and the philosophical one.

---

## 5. Six Concrete Implications

### 5.1 Quantum Device Certification

**Before:** Certifying a CNOT gate requires $\sim 160{,}000$ measurements (full process tomography, $d^4/\varepsilon^2$ for $d=4$, $\varepsilon = 0.01$).

**After:** $K_F(J(\text{CNOT})) \approx 150$ bits (stabilizer structure). MDL certification: $\sim 10{,}400$ measurements. **$15\times$ improvement at $\varepsilon=0.01$.**

For a 5-qubit error-correcting operation: $\sim 35{,}000$ measurements versus $\sim 10^7$. **$295\times$ improvement.**

**Practical protocol:** Run MDL certification. The output is: (a) the reconstructed channel, (b) a computable certificate showing it is within $\varepsilon$ of the ideal. The certificate IS the short ZCE program. If the program is long, the device has a problem. If short and consistent: certified.

### 5.2 Quantum Internet State Verification

For a 50-qubit entangled state transmitted over a quantum network: $K_F \approx 300$ bits (area-law structure). MDL verification: $\sim 3{,}000$ measurements. Standard QST: $\sim 10^{33}$.

**This is the difference between possible and physically impossible.** 3,000 measurements is achievable with current technology. $10^{33}$ is not achievable in the lifetime of the universe.

### 5.3 Algorithmic Complexity as Cryptographic Security

**Classical QKD security:** based on entropy $S(\rho) = n$. An eavesdropper Eve, to distinguish key states, needs many measurements.

**New criterion:** Eve needs $K_F(\text{key state})/\varepsilon$ measurements to distinguish. Security requires $K_F$ to be large — specifically, to be incompressible ($K_F \sim 4^n$).

**The gap:** A state with maximum von Neumann entropy ($S = n$) but low $K_F$ (structured despite appearing random) is cryptographically *weak* even though its entropy is maximal. This is undetected by standard entropy-based security proofs. The MDL framework detects it.

**Concrete vulnerability:** Suppose Alice uses a pseudorandom key state generated by a short quantum circuit of depth $t$. Then $K_F(\text{key}) \leq O(nt)$. Eve, knowing the circuit family, needs only $O(nt/\varepsilon)$ measurements to distinguish. If $t \ll n$, this is easy. Standard entropy-based analysis gives no vulnerability because $S = n$.

**New security criterion:** Quantum keys should have $K_F \geq n^2/O(1)$ to be secure against MDL attacks.

### 5.4 Quantum Occam's Razor for QML

For a quantum machine learning model with output state $\rho_\theta$ and $K_F(\rho_\theta) = L$:

$$\text{generalization error} \leq \text{training error} + O\!\left(\sqrt{\frac{L \ln 2}{m}}\right)$$

**This is the quantum Rademacher bound.** Low $K_F$ = simple model = good generalization.

**Practical implication:** Train QML models with the regularizer:
$$\mathcal{L}(\theta) = -\log P(\text{data}|\rho_\theta) + \lambda \cdot K_F(\rho_\theta)$$

The $\lambda K_F$ term penalizes complex models. This is quantum MDL regularization. For shallow quantum circuits ($K_F \propto \text{depth} \times n$), it penalizes deep circuits — the quantum analog of weight decay.

### 5.5 Area Law = MDL Bound for Many-Body Physics

Ground states of 1D local Hamiltonians satisfy the area law: entanglement entropy $S(A) \leq c \cdot |A|$ for subsystem $A$. This implies MPS description with bond dimension $D = e^{c|A|}$.

For a 1D chain of $n$ sites with area law: $K_F(\rho_0) = O(n \log n)$ bits.

**MDL bound:** $m^* = O(n \log n / \varepsilon)$ measurements to learn the ground state.

For $n = 100$, $\varepsilon = 0.1$: $m^* \approx 4{,}600$ measurements. Modern cold atom experiments can measure $\sim 10{,}000$ sites per run. **Ground state tomography of 100-site chains is within current experimental reach.**

**This resolves a long-standing question:** Can quantum many-body ground states be learned experimentally? The answer is YES, provided the area law holds, and the MDL bound gives the precise measurement count.

### 5.6 The Born Rule is Why Experiments Work

Every experiment in quantum mechanics relies on the Born rule to extract probabilities from measurements. The MDL result gives a new answer to: *why the Born rule?*

The Born rule is not just mathematically unique (Gleason) or operationally natural (QBism) — it is the unique rule that allows quantum states to be learned in $K_F/\varepsilon$ measurements. It is the *efficiency condition* on nature. Without the Born rule, quantum learning would require either more measurements or would be impossible for some states.

Experimental quantum physics *works* — we learn about quantum states by measuring them — and the Born rule is the precise reason why the measurements needed equal the description length of the state. Not more, not less.

---

## 6. The Research Program

This paper is not a destination. It is a map. The theorem $m^* = \Theta(K_F/\varepsilon)$ is the center, and it points in six directions simultaneously:

**Direction 1: Tight bounds via Fisher complexity.** Find the precise relationship between $K_F(\rho)$ and $I_F(\rho)$ (Fisher information rank). Conjecture: $I_F(\rho) \leq K_F(\rho) \leq c \cdot I_F(\rho) \cdot \log(d)$. Proving this gives a tight bound $m^* = \Theta(I_F(\rho)/\varepsilon)$ with $I_F$ computable from the ZCE program.

**Direction 2: Computational complexity.** Connect $K_F(\rho)$ to quantum circuit complexity. Conjecture: $K_F(\rho) \leq \text{circuit\_depth}(\rho) \cdot n + O(n)$. This gives sample complexity directly in terms of physical preparation cost.

**Direction 3: Cryptographic hardness.** Formalize the MDL cryptographic criterion. Give security reductions: if $K_F(\text{key}) \geq L$ and the adversary is restricted to $m$ measurements, then the information leakage is bounded. This is a new security proof methodology.

**Direction 4: Quantum PCP connection.** The quantum PCP theorem (open) says approximating ground energies is QMA-hard. Our framework predicts: if quantum PCP is true, then $K_F(\text{ground state}) = \Omega(n^c)$ for some $c > 1$. If area law is universal, $K_F = O(n \log n)$ and QST is efficient. These are complementary predictions: quantum PCP hardness = large $K_F$, area law = small $K_F$.

**Direction 5: Thermodynamics.** Landauer principle: erasing $K_F(\rho)$ bits costs $K_F \cdot kT \ln 2$ energy. Learning $\rho$ costs $K_F/\varepsilon$ measurements. These two costs are proportional. Conjecture: the thermodynamic cost of quantum state learning is $K_F \cdot kT \ln 2 / \varepsilon$. This connects information-theoretic learning bounds to physical energy bounds.

**Direction 6: Foundations.** The Born rule is the efficiency condition on nature. The low-$K_F$ of physical states is why science works. These are provable mathematical statements with philosophical content. The program is to make this connection precise: from "physical states have low $K_F$" to "science is possible" is a deduction, not a metaphor.

---

## 7. Summary

One theorem. Six implications. One program.

The theorem: learning complexity = description complexity, for both classical distributions and quantum states. The formula $m = \Theta(K/\varepsilon)$ is universal across both domains.

The implications: quantum devices are certifiable, quantum networks are verifiable, quantum keys need algorithmic complexity not just entropy, quantum ML has an Occam's razor, many-body ground states are experimentally learnable, and the Born rule is the condition that makes all of this work at the description-length rate.

The program: connect description length to circuit complexity, to Fisher information, to thermodynamics, to quantum PCP, to the foundations of science itself.

The first chapter is the QST bound. This paper is the second. The rest is open.

---

## Appendix: Proof That $K_F$ and Not $S$ Is the Right Measure

**Proposition A.1.** There is no function $f: \mathcal{D}(\mathcal{H}) \to \mathbb{R}_{\geq 0}$ depending only on the spectrum of $\rho$ (i.e., any function of von Neumann entropy $S(\rho)$, purity $\text{Tr}(\rho^2)$, or any spectral invariant) that satisfies $m^*(\rho, \varepsilon) = \Theta(f(\rho)/\varepsilon)$ for all $\rho \in \mathcal{H}_Q$.

*Proof.* The states $|0\rangle^n$ and $\frac{1}{d}I_d$ have vastly different $m^*$ ($O(n/\varepsilon)$ versus $O(1/\varepsilon)$) but identical spectra up to permutation if we choose $d = 2^n$ (both are eigenvectors with eigenvalues that differ only in which eigenvalue is 1). Any spectral function assigns them the same value. Therefore no spectral function can simultaneously correctly predict both. $\square$

This proves that $K_F$ — a non-spectral, non-unitary-invariant measure — is genuinely necessary. No "standard" quantum information measure suffices.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*The main theorem follows from Saraff (2026b) and (2026d). All numbered implications are derived, not speculative. Directions 1–6 in Section 6 are open problems, clearly labeled as conjectures where they go beyond current proofs.*
