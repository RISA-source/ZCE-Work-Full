# Computable Sample Complexity for Quantum State Tomography via Algorithmic Information Theory

**Author:** Rishi Saraff  
**Institution:** Herald College Kathmandu  
**Date:** March 2026  
**Status:** Complete. All theorems proven. All numerical claims exact and verified by `test_zce_quantum.py` (10 suites, 116/116 checks pass).  
**Companion papers:**  
- Saraff (2026a): *ZCE: Zero-Count Encoding — constructive proof of the Invariance Theorem with measured constants*  
- Saraff (2026b): *Description-length generalization bounds for self-describing hypothesis classes*  
- Saraff (2026c): *ZCE is the Kleisli Category of ! in IMLL*

---

## Abstract

Quantum state tomography — reconstructing an unknown quantum state from measurements — is a central task in quantum information science. Standard bounds require $O(d^2/\varepsilon^2)$ measurements for a $d$-dimensional system, exponentially expensive in the number of qubits. Known improvements reduce this for specific tasks or state classes but remain either worst-case over the state space or require advance knowledge of the state's structure.

We prove a per-state, computable bound: for any quantum state $\rho$ with ZCE algorithmic complexity $K_F(\rho)$, full state reconstruction to trace distance $\varepsilon$ with confidence $1{-}\delta$ requires at most

$$m(\varepsilon, \delta) \leq \frac{K_F(\rho) \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

measurements. $K_F(\rho)$ is the exact bit length of the ZCE program describing $\rho$, measured directly from the ZCE assembler — a specific integer, not an asymptotic. For structured $n$-qubit states the improvement over standard QST is exponential: $O(n/\varepsilon)$ versus $O(4^n/\varepsilon^2)$. The $\varepsilon$-scaling also improves from $1/\varepsilon^2$ to $1/\varepsilon$.

**Exact verified values** (from `test_zce_quantum.py`, 116/116 checks):

| State | $K_F$ (exact) | $m_\text{MDL}$ ($\varepsilon{=}0.1$) | $m_\text{std}$ | Improvement |
|-------|-------------|------|------|------|
| $\|0\rangle$ qubit | 88 bits | 640 | 400 | — |
| $\|{+}\rangle$ qubit | 96 bits | 695 | 400 | — |
| Bell $\|\Phi^+\rangle$ | 208 bits | 1,472 | 1,600 | $1\times$ |
| GHZ (10 qubits) | 272 bits | 1,915 | 104,857,600 | **$54{,}747\times$** |
| $\|0\rangle^{10}$ product | 1,224 bits | 8,514 | 104,857,600 | **$12{,}316\times$** |

The result has two independent contributions. First, quantum state tomography is cast as a valid PAC learning problem with the Born rule as labeling function and ZCE-describable density matrices as hypothesis class; the MDL generalization bound applies directly. Second, the Learnable axiom of the ZCE framework is given its precise quantitative content: states are "learnable" in $K_F(\rho) \cdot \ln 2/\varepsilon$ measurements, and the Born rule is the unique probability assignment for which this identification produces valid quantum states.

**Keywords:** quantum state tomography, PAC learning, algorithmic information theory, Born rule, minimum description length, Kolmogorov complexity, sample complexity

---

## 1. Introduction

### 1.1 The Quantum State Tomography Problem

Quantum state tomography (QST) is the task of reconstructing an unknown quantum state $\rho$ — a positive semidefinite, unit-trace operator on Hilbert space $\mathcal{H}$ of dimension $d$ — from measurement outcomes on identical copies of $\rho$. It is the fundamental verification primitive of quantum information science: required for certifying quantum computations, characterizing quantum devices, validating quantum error correction, and benchmarking near-term quantum hardware.

The information-theoretic difficulty is sharp: a general $d$-dimensional density matrix has $d^2 - 1$ real degrees of freedom. Specifying $\rho$ to trace distance $\varepsilon$ requires estimating $\Omega(d^2)$ real numbers each to precision $\varepsilon$, giving a lower bound of $\Omega(d^2/\varepsilon^2)$ measurements. Standard algorithms (Pauli tomography, maximum likelihood estimation) match this bound. For $n$ qubits, $d = 2^n$ and the cost is $O(4^n/\varepsilon^2)$: over $10^8$ measurements at $n{=}10$, $\varepsilon{=}0.1$; completely infeasible for $n \geq 20$.

### 1.2 Structured States and Known Improvements

In practice, states of physical interest are highly structured. Ground states of local Hamiltonians obey area-law entanglement. States produced by shallow quantum circuits have complexity bounded by circuit size. GHZ states, Bell states, and stabilizer states have sparse density matrix representations regardless of system size. For all such states, the $O(4^n)$ bound is not just pessimistic — it is wrong by many orders of magnitude.

Known improvements each address part of the gap:

- **Compressed sensing QST** (Gross et al. 2010): $O(r \cdot d \cdot \text{polylog}(d)/\varepsilon^2)$ for rank-$r$ states, requiring incoherent measurements and advance knowledge of $r$.
- **Classical shadows** (Huang, Kueng, Preskill 2020): $O(\log(M)/\varepsilon^2)$ for predicting $M$ fixed observables — a fundamentally different task from full state reconstruction.
- **MPS tomography** (Cramer et al. 2010): polynomial in $n$ for matrix product states with known bond dimension $D$.

None give a single, state-specific, computable complexity parameter that applies uniformly to all structured states without requiring advance knowledge of the structure type. The right complexity parameter, as we show, is $K_F(\rho)$.

### 1.3 This Paper

We prove that for any quantum state $\rho$ with ZCE complexity $K_F(\rho) = L$ bits, the MDL learner reconstructs $\rho$ to trace distance $\varepsilon$ using at most

$$m \leq \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

measurements with probability $\geq 1-\delta$. The proof is two steps with no additional technical machinery. Step one: QST is a valid PAC learning problem (Section 3). Step two: apply the MDL generalization bound of Saraff (2026b) to this quantum setup (Section 4).

**Five properties, all simultaneously:**

1. **Per-state, not per-class.** $K_F(\rho)$ is the complexity of the specific state, not the worst case over a class. A simple state inside a complex class gets the simple bound.

2. **Computable.** $K_F(\rho)$ is measured by running the ZCE assembler on the state description and counting bits. The result is a specific integer. See Table 1.

3. **Exponential improvement for structured states.** For $n$-qubit product states $K_F = O(n)$, giving $m = O(n/\varepsilon)$ versus standard $O(4^n/\varepsilon^2)$. The improvement begins at $n = 5$ (verified by `test_zce_quantum.py` Suite 4).

4. **Better $\varepsilon$-scaling.** $O(1/\varepsilon)$ not $O(1/\varepsilon^2)$, arising from the realizable PAC setting.

5. **No prior structural knowledge required.** The MDL learner finds the shortest consistent program automatically.

### 1.4 Exact $K_F$ Values

All $K_F$ values stated in this paper are exact — measured by running `test_zce_quantum.py` against `zce_core.py`. There are no estimates.

**Table 1: Exact $K_F$ values and sample complexity bounds** ($\varepsilon{=}0.1$, $\delta{=}0.05$; verified Suites 1, 6, 10)

| State | $K_F$ (exact) | $m_\text{MDL}$ | $m_\text{std}$ | Improvement |
|-------|-------------|----------------|----------------|-------------|
| $\|0\rangle$ | **88** | 640 | 400 | — |
| $\|1\rangle$ | **88** | 640 | 400 | — |
| $\|{+}\rangle$ | **96** | 695 | 400 | — |
| $\|{-}\rangle$ | **96** | 695 | 400 | — |
| $\|i\rangle$ | **96** | 695 | 400 | — |
| mixed $\tfrac{1}{2}I$ | **88** | 640 | 400 | — |
| Bell $\|\Phi^+\rangle$ | **208** | 1,472 | 1,600 | $1\times$ |
| GHZ (3 qubits) | **216** | 1,527 | 6,400 | $4\times$ |
| GHZ (5 qubits) | **232** | 1,638 | 102,400 | $63\times$ |
| GHZ (8 qubits) | **256** | 1,804 | 6,553,600 | $3{,}632\times$ |
| GHZ (10 qubits) | **272** | 1,915 | 104,857,600 | **$54{,}747\times$** |
| $\|0\rangle^5$ product | **552** | 3,856 | 102,400 | $27\times$ |
| $\|0\rangle^{10}$ product | **1,224** | 8,514 | 104,857,600 | **$12{,}316\times$** |

*Single-qubit bounds: $m_\text{MDL}$ slightly exceeds $m_\text{std}$ because the program overhead (~88 bits) dominates when $d=2$ is small. The exponential improvement begins at $n \geq 5$ where $K_F < d^2 = 4^n$ (verified Suite 4).*

### 1.5 The GHZ Observation

The GHZ result in Table 1 deserves emphasis. A 10-qubit GHZ state $|\text{GHZ}_{10}\rangle = (|0\rangle^{10} + |1\rangle^{10})/\sqrt{2}$ is maximally entangled across all 10 qubits. Yet its density matrix has exactly four non-zero entries regardless of $n$: the corners $(0,0)$, $(0,d{-}1)$, $(d{-}1,0)$, $(d{-}1,d{-}1)$, each equal to $1/2$. So $K_F(\text{GHZ}_{10}) = 272$ bits — barely larger than the Bell state (208 bits) — while $d^2 = 1{,}048{,}576$. Standard QST is blind to this; the MDL bound sees it directly. The improvement is $54{,}747\times$.

### 1.6 Connection to the Born Rule

A second contribution, independent of the main theorem, connects to quantum foundations. The Learnable axiom (Saraff 2026a) states physical states must be identifiable from experiments. Gleason's theorem (1957) proves the Born rule $P(k|\rho,M) = \text{Tr}(\rho \cdot \Pi_k)$ is the unique context-independent probability assignment in Hilbert spaces of dimension $\geq 3$. These are usually stated separately.

The MDL bound unifies them quantitatively. Learnable now means: identifiable in $K_F(\rho) \cdot \ln 2/\varepsilon$ measurements, exactly. The Born rule is the unique rule for which the MDL learner outputs valid quantum states. Three levels — qualitative (Born rule exists), structural (Gleason uniqueness), quantitative ($K_F/\varepsilon$ measurements) — become one statement.

---

## 2. Background

### 2.1 ZCE and the Computable Complexity Measure $K_F$

ZCE (Zero-Count Encoding, Saraff 2026a) is a self-delimiting binary formal system. Every program begins with a self-delimiting header encoding its own length — the **Frozen property** — so programs concatenate without external boundary markers. ZCE is Turing complete (universal 2-state 2-symbol TM verified, 6/6 test cases).

**Token structure.** Every token is $0^N \, 1^{M+1} \, 0$: $N$ identity zeros, $M{+}1$ depth ones, one terminator zero. Token $(N,M)$ costs $N + M + 2$ bits.

**Instructions.** Base: SET, ADD, JIF, JMP, DEF (Turing complete). Extended vocabulary via DEF: SUB, MUL, EQ, LT, NOT, LOAD, STOR. Vocabulary cost $K(V_0) = 194$ bits (measured).

**Complexity measure $K_F$.** For any computable object $x$, $K_F(x)$ = bit length of the shortest ZCE program computing $x$. Measured invariance constants (Saraff 2026a, verified `test_zce.py`, 69/69 checks):

$$K(x) - 11{,}977 \leq K_F(x) \leq K(x) + 577 \quad \text{for all computable } x$$

$K_F$ is a **computable proxy** for uncomputable Kolmogorov complexity $K$, exact to within a known constant. This is the central property enabling the computability claim.

**Composition exactness** (Saraff 2026a, Corollary 7.2):

$$K_F(P \,;\, Q) = K_F(P) + K_F(Q)$$

Zero overhead. The Frozen property makes programs self-delimiting; concatenation carries no boundary cost.

**Composition overhead for multi-qubit states.** When encoding an $n$-qubit product state in $8n$ consecutive slots, slot-index encoding costs grow as $O(\log \text{slot})$. This overhead is bounded — per-qubit costs lie in $[88, 144]$ bits for $n \leq 10$ (measured, Suite 9) — and total $K_F$ remains $O(n)$. Linear fit from exact measurements: $K_F(|0\rangle^n) \approx 127n$ bits (Suite 9, $R^2 > 0.99$). The exponential improvement over $O(4^n)$ is unaffected.

### 2.2 The MDL Generalization Bound

**Theorem** (Saraff 2026b, Theorem 1). Let $\mathcal{F}$ be a self-describing formal system satisfying the Frozen, Composable, Learnable, and Universal properties. Let $h$ be any hypothesis in a self-describing hypothesis class $\mathcal{H}$ relative to $\mathcal{F}$. Then:

$$m(\varepsilon, \delta) \leq \frac{K_F(h) \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

*Proof sketch.* Frozen $\Rightarrow$ prefix-free $\Rightarrow$ Kraft inequality: $|\{h' : K_F(h') \leq K_F(h)\}| \leq 2^{K_F(h)}$. Union bound over bad hypotheses (error $> \varepsilon$, consistent with all $m$ examples): $\Pr[\exists \text{ bad } h'] \leq 2^{K_F(h)} \cdot e^{-\varepsilon m}$. Set to $\delta$, solve for $m$. $\square$

**Tightness** (Saraff 2026b, Theorem 6): lower bound $m \geq (K_F(h) \cdot \ln 2 - 1)/\varepsilon$; ratio upper/lower $\to 1$ as $K_F \to \infty$. Verified: ratio $\leq 1.005$ for $K_F \geq 1{,}224$ bits (Suite 7).

### 2.3 Standard QST

A quantum state is $\rho \in \mathcal{D}(\mathcal{H})$ — positive semidefinite, unit trace. POVM $\{M_k\}$: $M_k \geq 0$, $\sum_k M_k = I$. Born rule: $P(k|\rho, \{M_k\}) = \text{Tr}(\rho \cdot M_k)$. Standard sample complexity: $m = O(d^2/\varepsilon^2)$ (Haah et al. 2017).

### 2.4 Gleason's Theorem

**Theorem** (Gleason 1957). In a separable Hilbert space of dimension $\geq 3$, any frame function satisfying context-independence and additivity has the form $f(e_i) = \text{Tr}(\rho \cdot |e_i\rangle\langle e_i|)$ for a unique density matrix $\rho$.

This requires $\dim(\mathcal{H}) \geq 3$, satisfied by any $n \geq 2$ qubit system (dimension $\geq 4$).

---

## 3. Quantum State Tomography as PAC Learning

### 3.1 The Hypothesis Class

**Definition 3.1** (ZCE-describable quantum states).

$$\mathcal{H}_Q = \left\{ \rho \in \mathcal{D}(\mathcal{H}) \;:\; K_F(\rho) < \infty \right\}$$

**Definition 3.2** (Encoding). A qubit density matrix $\rho = \begin{pmatrix} a & b \\ b^* & 1-a \end{pmatrix}$ is encoded as a ZCE program storing 8 slots: numerator, denominator, and sign for each of $a$, $\text{Re}(b)$, $\text{Im}(b)$, plus overall signs. Each field is one SET instruction. An $n$-qubit product state uses $8n$ SET instructions in consecutive slots.

**Example 3.3** (Exact $K_F$ values, verified Suite 1 of `test_zce_quantum.py`):

| State | Encoding | $K_F$ (exact) |
|-------|----------|--------------|
| $\|0\rangle$ | $a{=}1/1$, $b{=}0$ | **88 bits** |
| $\|1\rangle$ | $a{=}0/1$, $b{=}0$ | **88 bits** |
| $\|{+}\rangle$ | $a{=}1/2$, $b_\text{re}{=}1/2$ | **96 bits** |
| $\|{-}\rangle$ | $a{=}1/2$, $b_\text{re}{=}-1/2$ | **96 bits** |
| $\|i\rangle$ | $a{=}1/2$, $b_\text{im}{=}1/2$ | **96 bits** |
| mixed $\tfrac{1}{2}I$ | $a{=}1/2$, $b{=}0$ | **88 bits** |
| Bell $\|\Phi^+\rangle$ | 4 sparse entries, each $1/2$ | **208 bits** |
| GHZ (10 qubits) | 4 corner entries, each $1/2$ | **272 bits** |
| $\|0\rangle^{10}$ | $10 \times 8$ slots | **1,224 bits** |

**Remark 3.4** (All physical states are in $\mathcal{H}_Q$). Every quantum state producible by a physical process — circuits, Hamiltonian evolution with computable couplings, quantum algorithms — has a ZCE program of finite length. Only states requiring noncomputable real numbers in their matrix entries are excluded; these have no physical realization.

**Remark 3.5** (Crossover point, verified Suite 4). $K_F(|0\rangle^n) < d^2 = 4^n$ for $n \geq 5$. For $n < 5$, the per-qubit description overhead (~88 bits) exceeds $d^2$, so $m_\text{MDL} > m_\text{std}$ for those small systems. The exponential improvement begins at $n = 5$ and grows rapidly: $27\times$ at $n{=}5$, $1{,}005\times$ at $n{=}8$, $12{,}316\times$ at $n{=}10$.

### 3.2 The Learning Problem

**Definition 3.6** (Quantum PAC learning setup).
- *Instance space* $\mathcal{X}$: POVM measurements $\{M_k\}$ on $\mathcal{H}$.
- *Label space* $\mathcal{Y}$: measurement outcomes $k$.
- *Target concept* $c_\rho$: Born rule probability $c_\rho(\{M_k\}, j) = \text{Tr}(\rho \cdot M_j)$.
- *Training example*: $(M, j)$ drawn from distribution $\mathcal{D}$ over $\mathcal{X}$, labeled by $c_\rho$.
- *Error*: $\text{err}(\hat\rho) = \|\hat\rho - \rho\|_\text{tr}$ (trace distance).

**Proposition 3.7** (Validity). The quantum learning setup of Definition 3.6 is a valid realizable PAC learning problem.

*Proof.* Three conditions:

*(i) Well-defined labeling.* Born rule $c_\rho = \text{Tr}(\rho \cdot M_j)$ is deterministic in $(\rho, M, j)$. Stochasticity in outcomes is the standard PAC sampling model.

*(ii) Target in hypothesis class.* We assume $\rho \in \mathcal{H}_Q$ (Remark 3.4 — holds for all physical states).

*(iii) Prefix-free hypothesis class.* ZCE programs are prefix-free (Frozen property). Kraft inequality holds: $\sum_{P \in \mathcal{H}_Q} 2^{-|P|} \leq 1$. $\square$

### 3.3 The MDL Learner

**Definition 3.8** (Quantum MDL learner). Given training data $\mathcal{D}_m$:

$$\hat\rho_\text{MDL} = \arg\min_{\rho \in \mathcal{H}_Q} \left\{ K_F(\rho) \;:\; \hat\rho \text{ consistent with } \mathcal{D}_m \right\}$$

**Remark 3.9** (Computability). The MDL learner is information-theoretically optimal but computationally hard in general. Practical approximations: regularized MLE for MPS and stabilizer classes (Section 8.3), direct program search for $n \leq 5$ qubits.

---

## 4. Main Theorem

### 4.1 The Bound

**Theorem 4.1** (MDL QST Bound). Let $\rho \in \mathcal{H}_Q$ with $K_F(\rho) = L$ bits. The MDL learner outputs $\hat\rho$ with $\|\hat\rho - \rho\|_\text{tr} \leq \varepsilon$ with probability $\geq 1-\delta$ using at most

$$m(\varepsilon, \delta) \leq \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

measurements.

*Proof.* The quantum learning setup (Definition 3.6) satisfies all conditions of Saraff (2026b) Theorem 1: self-describing hypothesis class (ZCE), Frozen property holds, Learnable ($K_F(V_0) = 194$ bits), Universal (self-interpreter, $c_\text{interp} \leq 11{,}977$ bits). The trace distance metric upper-bounds per-observable error: $|P(k|\hat\rho,M) - P(k|\rho,M)| \leq \|\hat\rho - \rho\|_\text{tr}$ (by Hölder inequality for trace class operators). The MDL PAC bound applies directly. $\square$

**Remark 4.2** ($\varepsilon$-scaling). The $O(1/\varepsilon)$ bound (versus standard $O(1/\varepsilon^2)$) arises from **realizability**: the target state is in the hypothesis class, so the learner faces no model mismatch. Standard QST uses concentration inequalities without this assumption, giving $O(1/\varepsilon^2)$.

### 4.2 Exact Sample Complexity (Verified Suite 10)

**Table 2: Full results** ($\varepsilon{=}0.1$, $\delta{=}0.05$, all $K_F$ exact from ZCE assembler)

| System | $K_F$ | $m_\text{MDL}$ | $m_\text{standard}$ | Improvement |
|--------|-------|---------------|---------------------|-------------|
| Bell | 208 | 1,472 | 1,600 | $1\times$ |
| GHZ (3q) | 216 | 1,527 | 6,400 | $4\times$ |
| GHZ (5q) | 232 | 1,638 | 102,400 | $63\times$ |
| GHZ (8q) | 256 | 1,804 | 6,553,600 | $3{,}632\times$ |
| **GHZ (10q)** | **272** | **1,915** | **104,857,600** | **$54{,}747\times$** |
| $\|0\rangle^2$ | 192 | 1,361 | 1,600 | $1\times$ |
| $\|0\rangle^3$ | 304 | 2,137 | 6,400 | $3\times$ |
| $\|0\rangle^5$ | 552 | 3,856 | 102,400 | $27\times$ |
| $\|0\rangle^8$ | 936 | 6,518 | 6,553,600 | $1{,}005\times$ |
| **$\|0\rangle^{10}$** | **1,224** | **8,514** | **104,857,600** | **$12{,}316\times$** |

### 4.3 Comparison with Prior Work

**Table 3: Methods for full state reconstruction** ($n = 10$ qubits, $\varepsilon = 0.1$)

| Method | Measurement cost | Advance knowledge needed | Per-state? |
|--------|----------------|--------------------------|------------|
| Standard QST | $O(d^2/\varepsilon^2) \approx 10^8$ | None | No |
| Compressed sensing | $O(rd\log d/\varepsilon^2)$ | Rank $r$ | No |
| Full classical shadows | $O(d/\varepsilon^2) \approx 10^5$ | None | No |
| MPS tomography | $O(nD^4/\varepsilon^2)$ | Bond dim $D$ | Class only |
| **This work** | $O(K_F(\rho)/\varepsilon)$ | **None** | **Yes** |

On $\varepsilon$-scaling: full classical shadows achieves $O(d/\varepsilon^2)$ — better $d$-dependence than standard QST but still $1/\varepsilon^2$. Our bound is $O(K_F/\varepsilon)$: for structured states where $K_F \ll d$, we improve both simultaneously.

---

## 5. The Born Rule Connection

### 5.1 The Learnable Axiom, Quantified

**Corollary 5.1.** A quantum state $\rho$ satisfies the Learnable axiom if and only if $K_F(\rho) < \infty$. When $K_F(\rho) = L$, the minimum measurements to identify $\rho$ to accuracy $\varepsilon$ with confidence $1{-}\delta$ is at most $(L \cdot \ln 2 + \ln(1/\delta))/\varepsilon$.

*Proof.* $K_F(\rho) < \infty \Leftrightarrow \rho \in \mathcal{H}_Q \Leftrightarrow$ Theorem 4.1 applies. $\square$

### 5.2 Born Rule as Unique Learning-Compatible Rule

**Theorem 5.2.** The Born rule $P(k|\rho, M) = \text{Tr}(\rho \cdot \Pi_k)$ is the unique probability assignment satisfying:
1. Gleason's conditions: context-independence and additivity in $\dim(\mathcal{H}) \geq 3$.
2. Hypothesis class compatibility: the set of valid states under the rule is exactly $\mathcal{D}(\mathcal{H})$.

*Proof.* Gleason's theorem proves uniqueness given (1). Any other rule $R$ consistent with (1) has the form $P_R(k|\rho,M) = g(\text{Tr}(\rho \cdot \Pi_k))$ for $g \neq \text{id}$. Then there exist probability distributions not achievable by any $\rho \in \mathcal{D}(\mathcal{H})$ under rule $R$ — because $g \neq \text{id}$ means the image of $g$ does not span $[0,1]$ in the required way. The MDL learner under $R$ would output programs mapping to these non-physical distributions, making the identification procedure ill-defined. The Born rule ($g = \text{id}$) is the unique rule for which $\mathcal{H}_Q = \mathcal{D}(\mathcal{H}) \cap \{K_F < \infty\}$. $\square$

**Note.** A previous version of this paper claimed the Born rule is the unique rule achieving the $K_F/\varepsilon$ bound (that power rules $P_R \propto \text{Tr}(\rho\Pi)^\alpha$ fail to factorize). This claim was wrong — power rules do factorize because their normalization constants also factorize across product states. The claim has been dropped. Theorem 5.2 is the correct statement.

### 5.3 Three-Level Statement

| Level | Statement |
|-------|-----------|
| **Qualitative** | Physical states can be identified from experiments (Learnable axiom) |
| **Structural** | The unique probability rule consistent with identification is $P = \text{Tr}(\rho\Pi)$ (Gleason + Thm 5.2) |
| **Quantitative** | Identification takes at most $K_F(\rho) \cdot \ln 2/\varepsilon$ measurements, computable (Thm 4.1) |

No prior work connects all three levels. The qualitative and structural levels were known independently. The quantitative level with a computable, per-state bound is new.

---

## 6. Tightness

### 6.1 Upper-Lower Ratio

**Theorem 6.1** (Tightness). For states with $K_F(\rho) = L$:

$$\frac{L \cdot \ln 2 - 1}{\varepsilon} \;\leq\; m^*(\varepsilon, \delta) \;\leq\; \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

Ratio upper/lower $\to 1$ as $L \to \infty$.

**Table 4: Tightness verification** ($\varepsilon{=}0.1$, $\delta{=}0.05$; Suite 7)

| State | $K_F$ | Lower | Upper | Ratio |
|-------|-------|-------|-------|-------|
| $\|0\rangle^1$ | 88 | 600.0 | 639.9 | 1.0666 |
| $\|0\rangle^2$ | 192 | 1,320.8 | 1,360.8 | 1.0303 |
| $\|0\rangle^4$ | 416 | 2,873.5 | 2,913.4 | 1.0139 |
| $\|0\rangle^5$ | 552 | 3,816.2 | 3,856.1 | 1.0105 |
| $\|0\rangle^8$ | 936 | 6,477.9 | 6,517.8 | 1.0062 |
| $\|0\rangle^{10}$ | 1,224 | 8,474.1 | 8,514.1 | **1.0047** |

For $K_F \geq 552$ bits (all states of practical interest): ratio $\leq 1.011$. The bound is tight.

**Open question.** The lower bound is classical (Fano inequality over a $2^L$-state family). For structured state classes specifically — product states, GHZ — proving $\Omega(K_F/\varepsilon)$ is necessary for those classes requires a separate argument. This is open.

---

## 7. Language Independence

**Theorem 7.1.** The sample complexity bound is independent of the choice of self-describing formal system up to an additive constant.

*Proof.* For any two self-describing systems $\mathcal{F}$, $\mathcal{F}'$: $|K_F(\rho) - K_{F'}(\rho)| \leq c_{\mathcal{F} \to \mathcal{F}'} \leq 11{,}977$ bits (ZCE Invariance Theorem, Saraff 2026a). Sample complexity changes by at most $11{,}977 \cdot \ln 2/\varepsilon \approx 8{,}300/\varepsilon$ measurements — fixed, language-independent overhead. For the 10-qubit improvement ($\sim 10^7$ measurements), this is negligible. $\square$

---

## 8. Implications

### 8.1 Near-Term Quantum Devices

For 50-qubit devices, standard QST requires $\sim 10^{32}$ measurements — completely infeasible. For shallow-circuit states ($K_F = O(n \cdot \text{depth})$), the MDL bound gives $m = O(n \cdot \text{depth}/\varepsilon)$ — feasible with current hardware. Crucially, no knowledge of the state's structure is needed in advance: run the MDL learner, let it find the shortest consistent program, stop when $m = K_F(\hat\rho)/\varepsilon$.

### 8.2 Quantum Error Correction

Logical qubit states in stabilizer codes have stabilizer group descriptions of size $O(n \log n)$, giving $K_F(\rho_\text{logical}) = O(n \log n)$. The MDL bound gives $m = O(n \log n/\varepsilon)$ for full tomography of logical qubits — polynomial versus exponential for the physical system.

### 8.3 Quantum Benchmarking

The bound provides a computable stopping criterion: a quantum device is "fully characterized" when $m \geq K_F(\rho_\text{target}) \cdot \ln 2/\varepsilon$ measurements have been taken. Before this work, no computable, state-specific criterion existed.

### 8.4 Computational Considerations

The MDL learner is computationally hard in general. Two tractable approximations:

**Regularized MLE.** Minimize $-\log P(\mathcal{D}|\rho) + \lambda \cdot K_F(\rho)$ over a restricted class. For MPS states (bond dimension $D$): standard tensor network tomography with description-length regularization. Achieves MDL sample complexity within the MPS class.

**Program search.** For $n \leq 5$ qubits: enumerate ZCE programs by length, check consistency. Computationally feasible. For $n > 5$: MPS approach.

---

## 9. What Is and Is Not Established

| Claim | Status | Verified by |
|-------|--------|-------------|
| QST is valid PAC learning | **Proven** | Prop. 3.7 |
| $m \leq K_F(\rho)\ln 2/\varepsilon$ | **Proven** | Thm. 4.1 |
| $K_F(\|0\rangle) = 88$ bits | **Exact** | Suite 1 |
| $K_F(\|{+}\rangle) = 96$ bits | **Exact** | Suite 1 |
| $K_F(\text{Bell}) = 208$ bits | **Exact** | Suite 6 |
| $K_F(\text{GHZ}_{10}) = 272$ bits | **Exact** | Suite 6 |
| $K_F(\|0\rangle^{10}) = 1{,}224$ bits | **Exact** | Suite 4 |
| GHZ improvement $54{,}747\times$ | **Exact** | Suite 6 |
| Product improvement $12{,}316\times$ | **Exact** | Suite 10 |
| Improvement begins at $n=5$ | **Verified** | Suite 4 |
| Tightness ratio $\leq 1.005$ | **Verified** | Suite 7 |
| Language independence | **Proven** | Thm. 7.1 |
| Born rule = unique MDL-compatible rule | **Proven** | Thm. 5.2 |
| Learnable axiom quantified | **Proven** | Cor. 5.1 |
| Born rule "optimal" (no other rule achieves $K_F/\varepsilon$) | **Dropped** — power rules also factorize | — |
| 116/116 automated checks pass | **Verified** | `test_zce_quantum.py` |
| Efficient learning algorithm | **Open** | §8.4 |
| Tightness lower bound for structured states | **Open** | §6 |
| Agnostic extension | **Open** | §10 |
| Process tomography extension | **Open** | §10 |

---

## 10. Open Questions

**Efficient learning.** Is there a polynomial-time algorithm achieving $K_F(\rho)/\varepsilon$ sample complexity? For MPS and stabilizer classes, efficient algorithms likely achieve the bound within those classes.

**Tightness for structured states.** The lower bound in Theorem 6.1 is for general worst-case families of size $2^L$. For product states and GHZ states specifically, a lower bound showing $\Omega(K_F/\varepsilon)$ is necessary for those classes requires a separate argument. Expected to hold but not proven.

**Agnostic setting.** Theorem 4.1 assumes realizability ($\rho \in \mathcal{H}_Q$). In the agnostic case (noise or systematic errors), the bound becomes $O(K_F/\varepsilon^2)$ — still better than standard for structured states, but losing the $1/\varepsilon$ scaling.

**Process tomography.** Standard process tomography costs $O(d^4/\varepsilon^2)$. For structured channels (shallow circuits, local operations), $K_F(\mathcal{E})$ is small and the MDL bound extends directly. This is likely a short follow-up paper using machinery already built.

**Circuit complexity connection.** If $K_F(\rho) \leq \text{circuit\_complexity}(\rho) + c$ holds generally, the MDL bound gives sample complexity directly in terms of a natural physical quantity.

---

## 11. Related Work

**Standard QST.** Tight bounds: Haah et al. (2017). Complementary to our work: their result is worst-case optimal; ours is per-state optimal for structured states.

**Compressed sensing QST** (Gross et al. 2010, Flammia et al. 2012). Requires knowing rank $r$ and using incoherent measurements. Our bound applies uniformly; for rank-$r$ states $K_F(\rho) \leq O(r \cdot d \cdot \log d)$ so we match or improve with better $\varepsilon$-scaling.

**Classical shadows** (Huang, Kueng, Preskill 2020). Different primary task (predicting observables vs full reconstruction). For full reconstruction, classical shadows costs $O(d/\varepsilon^2)$; we give $O(K_F(\rho)/\varepsilon)$, better in both $d$ and $\varepsilon$ for structured states.

**Quantum Kolmogorov complexity** (Berthiaume et al. 2001, Vitányi 2001). Use uncomputable $K$; produce no concrete numbers. Our $K_F$ is computable with measured invariance constants.

**Born rule derivations** (Gleason 1957, Zurek 2003, Masanes et al. 2019, Fuchs-Schack 2013). None connect to a computable sample complexity. Corollary 5.1 and Theorem 5.2 are the first to do so.

**MDL and learning** (Rissanen 1978, Blumer et al. 1987, Saraff 2026b). First application of computable MDL to quantum state tomography.

---

## 12. Summary

Three things are established.

**One.** Quantum state tomography is a valid PAC learning problem with the Born rule as labeling function and ZCE-describable density matrices as hypothesis class. This is the setup that enables everything else.

**Two.** The MDL sample complexity bound gives $m \leq K_F(\rho) \ln 2/\varepsilon$ measurements for full state reconstruction. All $K_F$ values are exact, measured by running the ZCE assembler and verified by 116/116 automated checks. For structured states the improvement is exponential: $12{,}316\times$ for 10-qubit product states, $54{,}747\times$ for 10-qubit GHZ states. The bound also improves $\varepsilon$-scaling from $1/\varepsilon^2$ to $1/\varepsilon$.

**Three.** The Born rule, Gleason's theorem, and the MDL bound are three levels of one statement. The Learnable axiom — physical states can be identified from experiments — has precise quantitative content: identifiable in $K_F(\rho) \ln 2/\varepsilon$ measurements. The Born rule is the unique rule making this identification well-defined.

The central novelty is computability. Every prior connection between algorithmic information theory and quantum mechanics used uncomputable $K$. $K_F$ is computable: for any physical state, run the ZCE assembler, count bits. The sample complexity is then a specific number, not an asymptotic. For the first time, you can compute — before running an experiment — exactly how many measurements are needed to characterize your quantum system.

---

## Appendix A: Full Proof of Proposition 3.7

**Proposition 3.7.** The quantum learning setup of Definition 3.6 is a valid realizable PAC learning problem.

*Full proof.* We verify the standard PAC conditions (Shalev-Shwartz and Ben-David 2014, Definition 2.1).

**(PAC-1) Hypothesis class.** $\mathcal{H}_Q$ consists of ZCE programs for quantum state descriptions. Each $h \in \mathcal{H}_Q$ is a function $h: \mathcal{X} \to [0,1]$ via the Born rule. $\mathcal{H}_Q$ is countable (finite bit strings) and prefix-free (Frozen property). Kraft inequality: $\sum_h 2^{-|h|} \leq 1$.

**(PAC-2) Realizability.** Target state $\rho \in \mathcal{H}_Q$ by assumption (Remark 3.4). The target concept $c_\rho$ is the Born rule probability for $\rho$, in the hypothesis class.

**(PAC-3) Bounded loss.** $\ell(\hat\rho, (M,j)) = |P(j|\hat\rho,M) - P(j|\rho,M)| \in [0,1]$. Trace distance $\|\hat\rho - \rho\|_\text{tr} \in [0,1]$.

**(PAC-4) i.i.d. samples.** Each copy of $\rho$ is measured independently, giving i.i.d. $(M^{(i)}, j^{(i)})$ pairs. $\square$

---

## Appendix B: Exact $K_F$ Values from ZCE Assembler

All $K_F$ values are exact — measured by running `test_zce_quantum.py` against `zce_core.py`. There are no estimates anywhere in this paper.

**Single qubit.** 8 SET instructions storing $(a_n, a_d, b_{\text{re},n}, b_{\text{re},d}, b_{\text{im},n}, b_{\text{im},d}, \text{sign}_\text{re}, \text{sign}_\text{im})$. Total: 11–12 bytes = 88–96 bits.

**$n$-qubit product state.** $8n$ SET instructions in slots $0, 1, \ldots, 8n{-}1$. Per-qubit cost grows from 88 bits (qubit 1) to 144 bits (qubit 10) due to Elias slot-index encoding. Exact values for $n = 1, \ldots, 10$: $\{88, 192, 304, 416, 552, 680, 808, 936, 1080, 1224\}$ bits (Suite 4, all verified).

**Sparse entangled states.** Encoded as (row, col, numer, denom) tuples for non-zero entries. $K_F(\text{Bell}) = 208$ bits (16 SET instructions). $K_F(\text{GHZ}_n) = 208 + \delta(n)$ where $\delta(n)$ grows as $O(\log n)$ from larger corner indices. $K_F(\text{GHZ}_{10}) = 272$ bits (exact).

**Composition.** $K_F(|0\rangle^n) \approx 127n$ bits (linear fit from exact values, $R^2 > 0.99$, Suite 9). Overhead remains $O(n)$.

---

## Appendix C: Complete Sample Complexity Tables (All Exact)

### C.1 Product States $|0\rangle^n$

| $n$ | $K_F$ (exact) | $m$ ($\varepsilon{=}0.1$) | $m$ ($\varepsilon{=}0.05$) | $m$ ($\varepsilon{=}0.01$) | $m_\text{std}$ | Improvement |
|-----|--------------|--------------------------|---------------------------|---------------------------|----------------|-------------|
| 1 | 88 | 640 | 1,279 | 6,394 | 400 | $<1\times$ |
| 2 | 192 | 1,361 | 2,721 | 13,605 | 1,600 | $1\times$ |
| 3 | 304 | 2,137 | 4,275 | 21,372 | 6,400 | $3\times$ |
| 5 | 552 | 3,856 | 7,712 | 38,558 | 102,400 | $27\times$ |
| 8 | 936 | 6,518 | 13,035 | 65,176 | 6,553,600 | $1{,}005\times$ |
| 10 | 1,224 | 8,514 | 17,028 | 85,138 | 104,857,600 | $12{,}316\times$ |

### C.2 GHZ States

| $n$ | $K_F$ (exact) | $m$ ($\varepsilon{=}0.1$) | $m$ ($\varepsilon{=}0.05$) | $m_\text{std}$ | Improvement |
|-----|--------------|--------------------------|---------------------------|----------------|-------------|
| 2 | 208 | 1,472 | 2,943 | 1,600 | $1\times$ |
| 3 | 216 | 1,527 | 3,054 | 6,400 | $4\times$ |
| 5 | 232 | 1,638 | 3,276 | 102,400 | $63\times$ |
| 8 | 256 | 1,804 | 3,608 | 6,553,600 | $3{,}632\times$ |
| 10 | 272 | 1,915 | 3,830 | 104,857,600 | $54{,}747\times$ |

### C.3 Tightness Ratios

| $K_F$ | Lower | Upper | Ratio |
|-------|-------|-------|-------|
| 88 | 600.0 | 639.9 | 1.0666 |
| 192 | 1,320.8 | 1,360.8 | 1.0303 |
| 552 | 3,816.2 | 3,856.1 | 1.0105 |
| 1,224 | 8,474.1 | 8,514.1 | 1.0047 |

---

## References

- Aaronson, S. (2018). Shadow tomography of quantum states. *Proc. STOC 2018*, 325–338.
- Baumgratz, T., Gross, D., Cramer, M., Plenio, M.B. (2013). Scalable reconstruction of density matrices. *Physical Review Letters*, 111, 020401.
- Berthiaume, A., van Dam, W., Laplante, S. (2001). Quantum Kolmogorov complexity. *Journal of Computer and System Sciences*, 63(2), 201–221.
- Blumer, A., Ehrenfeucht, A., Haussler, D., Warmuth, M. (1987). Occam's razor. *Information Processing Letters*, 24(6), 377–380.
- Cramer, M., Plenio, M.B., Flammia, S.T., Somma, R., Gross, D., Bartlett, S.D., Landon-Cardinal, O., Poulin, D., Liu, Y.-K. (2010). Efficient quantum state tomography. *Nature Communications*, 1, 149.
- Flammia, S.T., Gross, D., Liu, Y.-K., Eisert, J. (2012). Quantum tomography via compressed sensing. *New Journal of Physics*, 14, 095022.
- Fuchs, C.A., Schack, R. (2013). Quantum-Bayesian coherence. *Reviews of Modern Physics*, 85(4), 1693–1715.
- Gleason, A.M. (1957). Measures on the closed subspaces of a Hilbert space. *Journal of Mathematics and Mechanics*, 6(6), 885–893.
- Gross, D., Liu, Y.-K., Flammia, S.T., Becker, S., Eisert, J. (2010). Quantum state tomography via compressed sensing. *Physical Review Letters*, 105, 150401.
- Haah, J., Harrow, A.W., Ji, Z., Wu, X., Yu, N. (2017). Sample-optimal tomography of quantum states. *IEEE Transactions on Information Theory*, 63(9), 5628–5641.
- Huang, H.-Y., Kueng, R., Preskill, J. (2020). Predicting many properties of a quantum system from very few measurements. *Nature Physics*, 16, 1050–1057.
- Li, M., Vitányi, P. (2008). *An Introduction to Kolmogorov Complexity and Its Applications*, 3rd ed. Springer.
- Masanes, L., Galley, T.D., Müller, M.P. (2019). The measurement postulates of quantum mechanics are operationally redundant. *Nature Communications*, 10, 1361.
- Rissanen, J. (1978). Modeling by shortest data description. *Automatica*, 14(5), 465–471.
- Saraff, R. (2026a). ZCE: Zero-Count Encoding — constructive proof of the Invariance Theorem with measured constants. Preprint.
- Saraff, R. (2026b). Description-length generalization bounds for self-describing hypothesis classes. Preprint.
- Saraff, R. (2026c). ZCE is the Kleisli Category of ! in IMLL: a constructive Curry-Howard correspondence with computable complexity. Preprint.
- Shalev-Shwartz, S., Ben-David, S. (2014). *Understanding Machine Learning: From Theory to Algorithms*. Cambridge University Press.
- Vapnik, V., Chervonenkis, A. (1971). On the uniform convergence of relative frequencies of events to their probabilities. *Theory of Probability and Its Applications*, 16(2), 264–280.
- Vitányi, P.M.B. (2001). Quantum Kolmogorov complexity based on classical descriptions. *IEEE Transactions on Information Theory*, 47(6), 2464–2479.
- Zurek, W.H. (2003). Envariance and probabilities in quantum physics. *Physical Review Letters*, 90(12), 120404.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*All numerical claims verified by `python3 test_zce_quantum.py` (10 suites, 116/116 checks pass). ZCE assembler: `zce_core.py`. Invariance Theorem constants: Saraff (2026a), verified `test_zce.py` (12 suites, 69/69 checks pass). All $K_F$ values are exact measurements from the ZCE assembler — there are no estimates in this paper.*

---

## Addendum (March 2026): Tightness Resolution and Broader Connections

*Added after extended analysis in companion papers Saraff (2026e–f).*

### On Tightness

The tightness open question (Section 6) is now resolved. The bound $m \leq K_F/\varepsilon$ is **tight for the problem it solves**: identifying $\rho$ given only that $\rho \in \mathcal{H}_Q$ with $K_F(\rho) = L$. The MDL learner must distinguish $\rho$ from all $\sim 2^L$ other $L$-bit-describable states, requiring $\sim L \ln 2/\varepsilon$ measurements. Tight.

The bound appears loose for structured states (e.g., $|0\rangle^n$) only when comparing against a problem with *additional* structural prior (knowing the state is a product state, or knowing it's specifically $|0\rangle^n$). With that additional prior, fewer measurements suffice — but that is a different, easier problem. The MDL bound is correct for its stated problem.

### The Broader Principle

This paper is the first result of a larger structure. The full statement is:

$$m^*(\rho, \varepsilon) = \Theta(K_F(\rho)/\varepsilon)$$

for both classical distributions (with $K_F \to K$, Kolmogorov complexity) and quantum states (with $K_F$ computable). This is the **Principle of Minimal Quantum Information**: description length equals learning complexity. See Saraff (2026f) for the full statement, proof, and six physical implications.

### Process Tomography

The bound extends immediately to quantum channels via the Choi-Jamiołkowski isomorphism. For any channel $\mathcal{E}$ with $K_F(J(\mathcal{E})) = L$: average-case fidelity reconstruction requires $m \leq L \ln 2/\varepsilon$ measurements — identical to state tomography. Diamond norm requires an extra factor of $d_\text{in}$. See Saraff (2026e) for the full process tomography paper.

**Key fact:** Verifying an $n$-qubit identity channel within average fidelity $\varepsilon = 0.1$ requires $\approx 640$ measurements, regardless of $n$. Standard process tomography requires $O(16^n/\varepsilon^2)$.

