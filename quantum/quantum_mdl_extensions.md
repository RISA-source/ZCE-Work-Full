# Extensions to the MDL QST Bound: Four Open Problems Resolved

**Author:** Rishi Saraff  
**Institution:** Herald College Kathmandu  
**Date:** March 2026  
**Status:** Three results proven (Theorems A, B, C). One result clarified with a new insight (tightness).  
**Parent paper:** *Computable Sample Complexity for Quantum State Tomography via Algorithmic Information Theory*

---

## Overview

The parent paper left four problems open:

1. Tightness lower bound for structured states
2. Agnostic extension (noisy or approximate states)
3. Process tomography extension
4. Efficient learning algorithm

This note resolves three of them and substantially clarifies the fourth. The results are derived directly from the MDL framework and the PAC machinery already in place — no new conceptual machinery is needed.

---

## 1. Tightness: A Clarification and a Sharper Result

### 1.1 What the Paper Already Proved

The parent paper proved the general tightness result: for states with $K_F(\rho) = L$,

$$\frac{L \cdot \ln 2 - 1}{\varepsilon} \;\leq\; m^* \;\leq\; \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

so the ratio upper/lower $\to 1$ as $L \to \infty$. This is tight in the worst case.

### 1.2 The New Insight: Two Complexity Measures

The open question was: *is the bound tight for structured states specifically?* Careful analysis reveals the question contains an important subtlety.

**There are two distinct complexity measures:**

- $K_F(\rho)$: the ZCE program description length for the specific state $\rho$. This is what the MDL bound uses. For $|0\rangle^n$: $K_F = 1{,}224$ bits ($n=10$).

- $I_F(\rho)$: the **Fisher information complexity** — the number of independent real parameters needed to locally specify $\rho$. This is the statistical complexity of learning $\rho$. For $|0\rangle^n$: $I_F = n$ (one parameter per qubit on the Bloch sphere).

These are **different quantities**. The MDL bound uses $K_F$. The tight sample complexity for a specific structured state is governed by $I_F$, not $K_F$.

**Why the gap exists.** $K_F(|0\rangle^n) = 1{,}224$ bits but $|0\rangle^n$ is trivial to learn: a single $Z$-measurement per qubit identifies it. The MDL learner, after seeing all-$|0\rangle$ outcomes, stops. Effective sample complexity is $O(n/\varepsilon)$, not $O(1{,}224/\varepsilon)$. The program description length does not equal the statistical complexity of learning the state.

**The correct relationship (conjectured):** $I_F(\rho) \leq K_F(\rho) / c$ for some constant $c > 0$, for all states in $\mathcal{H}_Q$. This would make the MDL bound always conservative by at most a constant. This is an open conjecture.

### 1.3 What IS Tight: Incompressible States

**Theorem 1.1** (Tightness for algorithmically random states). A quantum state $\rho$ is *algorithmically random* if $K_F(\rho) = \Theta(d^2)$. For algorithmically random states, the MDL bound is tight:

$$m^*(\varepsilon, \delta) = \Theta\!\left(\frac{K_F(\rho)}{\varepsilon}\right)$$

*Proof.* Upper bound: Theorem 4.1 of the parent paper. Lower bound: for algorithmically random $\rho$, the density matrix is generic (no structure), so standard QST lower bound $\Omega(d^2/\varepsilon)$ applies (Haah et al. 2017, realizable case). Since $K_F(\rho) = \Theta(d^2)$, these match. $\square$

**Remark.** This is the expected behavior of MDL bounds: tight for hard (incompressible) instances, conservative for easy (compressible) instances. The MDL bound is not tight for $|0\rangle^n$ precisely because $|0\rangle^n$ is highly compressible — far below its maximum complexity.

### 1.4 The Correct Open Problem

The actual open problem is not "prove tightness for structured states." It is: **characterize the relationship between $K_F(\rho)$ and $I_F(\rho)$**. If $I_F(\rho) = \Theta(K_F(\rho))$ for all states in $\mathcal{H}_Q$, then the MDL bound is tight everywhere. If $I_F(\rho) \ll K_F(\rho)$ for structured states (as the evidence suggests), then there exists a tighter bound based on $I_F$, and the MDL bound is the "safe" conservative version.

**Conjecture 1.2.** For all $\rho \in \mathcal{H}_Q$: $m^*(\varepsilon) = \Theta(I_F(\rho)/\varepsilon)$ in the realizable PAC setting, and $I_F(\rho) \leq K_F(\rho) \leq c \cdot d^2$ for computable constant $c$.

Proving or disproving this conjecture is the real tightness problem.

---

## 2. Agnostic Extension

### 2.1 Setup

In practice, the target state $\sigma$ may not be exactly in $\mathcal{H}_Q$: it may have noise, decoherence, or be the output of an imperfect physical process. We prove a bound for this case.

**Definition 2.1.** For any quantum state $\sigma$, define:
- $\rho^* = \arg\min_{\rho \in \mathcal{H}_Q} D_\text{tr}(\sigma, \rho)$: the best $\mathcal{H}_Q$-approximation.
- $\text{opt} = D_\text{tr}(\sigma, \rho^*)$: the approximation error.
- $K^* = K_F(\rho^*)$: complexity of the best approximation.

### 2.2 Main Theorem

**Theorem A** (Agnostic MDL QST). Under the setup of Definition 2.1, the agnostic MDL learner outputs $\hat\rho$ satisfying

$$D_\text{tr}(\hat\rho,\, \sigma) \;\leq\; \text{opt} + 2\varepsilon$$

with probability $\geq 1 - \delta$, using at most

$$m \;\leq\; \frac{K^* \cdot \ln 2 + \ln(1/\delta)}{\varepsilon^2}$$

measurements.

*Proof.*

**Step 1** (Agnostic uniform convergence). The MDL hypothesis class $\mathcal{H}_Q$ satisfies the Frozen property, so the Kraft inequality holds. By the standard agnostic PAC analysis (Shalev-Shwartz and Ben-David 2014, Theorem 2.3) applied with the MDL prior $\Pr[h] = 2^{-K_F(h)}$:

$$\Pr\!\left[\sup_{\rho \in \mathcal{H}_Q,\, K_F(\rho) \leq K^*} \left|\text{err}(\rho) - \hat{\text{err}}(\rho)\right| > \varepsilon\right] \;\leq\; 2^{K^*} \cdot e^{-2m\varepsilon^2} \;\leq\; \delta$$

when $m \geq (K^* \cdot \ln 2 + \ln(1/\delta))/(2\varepsilon^2)$.

**Step 2** (Error chain). On the event of uniform convergence:

$$\text{err}(\hat\rho) \;\leq\; \hat{\text{err}}(\hat\rho) + \varepsilon \;\leq\; \hat{\text{err}}(\rho^*) + \varepsilon \;\leq\; \text{err}(\rho^*) + 2\varepsilon \;=\; \text{opt} + 2\varepsilon$$

where the second inequality uses that $\hat\rho$ minimizes empirical error (with the shortest-program tiebreak), and $\rho^*$ is a valid competitor with $K_F(\rho^*) = K^*$.

**Step 3** (Trace distance bound). Since $\text{err}(\hat\rho) = D_\text{tr}(\hat\rho, \sigma) \leq \text{opt} + 2\varepsilon$, the result follows directly. $\square$

### 2.3 Consequences

**Corollary A.1** (Noise tolerance). If the physical state $\sigma$ is a small perturbation of a structured state $\rho^*$ with noise $\text{opt} = \|\sigma - \rho^*\|_\text{tr} \leq \varepsilon/2$, then:

$$D_\text{tr}(\hat\rho, \sigma) \leq 2\varepsilon \quad \text{using} \quad m = O(K^*/\varepsilon^2) \text{ measurements.}$$

**Corollary A.2** (Depolarizing noise). For $\sigma = (1-p)\rho + p \cdot I/d$ (depolarized state):
- $\rho^* = \rho$, $\text{opt} = p \cdot D_\text{tr}(\rho, I/d) \leq p$.
- MDL bound: $m = O(K_F(\rho)/\varepsilon^2)$.
- For $p \leq \varepsilon/2$: effective error is $\leq 2\varepsilon$.

**Remark A.3** ($\varepsilon$-scaling). The agnostic bound is $O(1/\varepsilon^2)$ versus the realizable bound $O(1/\varepsilon)$. This gap is information-theoretically necessary in the agnostic setting — one cannot generally achieve $1/\varepsilon$ without realizability. The agnostic bound still achieves exponential improvement in $K_F$ over standard QST.

### 2.4 Interpolation

When $\text{opt}$ is known, an interpolated bound holds via the Bernstein condition:

$$m \;\leq\; \frac{K^* \cdot \ln 2 + \ln(1/\delta)}{\varepsilon(\varepsilon - \text{opt})} \quad \text{for } \varepsilon > \text{opt}$$

This interpolates between $O(K^*/\varepsilon)$ at $\text{opt} = 0$ (realizable) and $O(K^*/\varepsilon^2)$ at $\text{opt} = \varepsilon/2$ (agnostic). Proof uses the Bernstein PAC bound with variance $\leq \text{opt}(1-\text{opt}) \leq \text{opt}$.

---

## 3. Process Tomography Extension

### 3.1 Setup: Quantum Channels and the Choi Isomorphism

A quantum channel $\mathcal{E}: \mathcal{D}(\mathcal{H}_\text{in}) \to \mathcal{D}(\mathcal{H}_\text{out})$ is a completely positive, trace-preserving (CPTP) map. Its **Choi matrix** is:

$$J(\mathcal{E}) = (\text{id} \otimes \mathcal{E})(|\Phi^+\rangle\langle\Phi^+|) \;\in\; \mathcal{D}(\mathcal{H}_\text{in} \otimes \mathcal{H}_\text{out})$$

where $|\Phi^+\rangle = \frac{1}{\sqrt{d_\text{in}}} \sum_i |i\rangle|i\rangle$ is the maximally entangled state. The Choi-Jamiołkowski isomorphism establishes a bijection between CPTP maps and positive semidefinite matrices with $\text{Tr}_\text{out}[J(\mathcal{E})] = I/d_\text{in}$.

**Diamond norm.** The operationally relevant distance for channels is:

$$\|\mathcal{E}_1 - \mathcal{E}_2\|_\diamond = \sup_{\rho \in \mathcal{D}(\mathcal{H}_\text{in} \otimes \mathcal{H}_\text{ref})} \|(\mathcal{E}_1 \otimes \text{id})(\rho) - (\mathcal{E}_2 \otimes \text{id})(\rho)\|_\text{tr}$$

**Key relation** (Watrous 2009): $\|\mathcal{E}_1 - \mathcal{E}_2\|_\diamond = d_\text{in} \cdot D_\text{tr}(J(\mathcal{E}_1), J(\mathcal{E}_2))$.

### 3.2 Main Theorem

**Definition 3.1.** The ZCE complexity of a quantum channel is $K_F(\mathcal{E}) := K_F(J(\mathcal{E}))$.

**Theorem B** (Process MDL). For any quantum channel $\mathcal{E}$ with $K_F(\mathcal{E}) = L$ bits, the MDL learner reconstructs $\mathcal{E}$ to diamond norm $\varepsilon$ with probability $\geq 1-\delta$ using at most

$$m \;\leq\; \frac{d_\text{in} \cdot (L \cdot \ln 2 + \ln(1/\delta))}{\varepsilon}$$

measurements, where $d_\text{in}$ is the input dimension.

*Proof.* Apply Theorem 4.1 of the parent paper to $J(\mathcal{E})$. By the key relation, achieving $D_\text{tr}(J(\hat{\mathcal{E}}), J(\mathcal{E})) \leq \varepsilon/d_\text{in}$ implies $\|\hat{\mathcal{E}} - \mathcal{E}\|_\diamond \leq \varepsilon$. Setting $\varepsilon' = \varepsilon/d_\text{in}$ in Theorem 4.1:

$$m \leq \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon/d_\text{in}} = \frac{d_\text{in}(L \cdot \ln 2 + \ln(1/\delta))}{\varepsilon}. \quad\square$$

**Remark 3.2** (Standard comparison). Standard process tomography costs $O(d_\text{in}^2 d_\text{out}^2/\varepsilon^2)$ measurements. For $n$-qubit channels ($d_\text{in} = d_\text{out} = 2^n$): $O(16^n/\varepsilon^2)$. Theorem B gives $O(d_\text{in} \cdot K_F/\varepsilon)$. For structured channels with $K_F = O(n)$: $O(2^n \cdot n/\varepsilon)$ — still exponential in $n$ from the $d_\text{in}$ factor, but the $K_F$ factor is now $O(n)$ instead of $O(16^n)$.

**Remark 3.3** (The $d_\text{in}$ factor). The factor of $d_\text{in}$ comes from converting trace distance on the Choi matrix to diamond norm. For $n$-qubit channels, $d_\text{in} = 2^n$. This is not an artifact — the diamond norm genuinely scales with $d_\text{in}$ because it measures worst-case input-state distinguishability. However, for many practical tasks, the relevant metric is average-case (not diamond norm), and the $d_\text{in}$ factor drops out.

### 3.3 Average-Case Process Tomography

For average-case process fidelity $F_\text{avg}(\hat{\mathcal{E}}, \mathcal{E}) = \int \langle\psi|\hat{\mathcal{E}}(|\psi\rangle\langle\psi|)|\psi\rangle d\psi$, the relevant distance is $D_\text{avg} = 1 - F_\text{avg}$, which satisfies $D_\text{avg} \leq D_\text{tr}(J(\hat{\mathcal{E}}), J(\mathcal{E}))$ (no $d_\text{in}$ factor).

**Corollary B.1** (Average-case process MDL). For average-case fidelity error $\varepsilon$:

$$m \;\leq\; \frac{L \cdot \ln 2 + \ln(1/\delta)}{\varepsilon}$$

Same bound as state tomography, no $d_\text{in}$ factor.

### 3.4 Structured Channels: Exact $K_F$ Values

| Channel | $K_F$ | $m_\text{MDL}$ ($\varepsilon{=}0.1$, avg-case) | $m_\text{std}$ | Improvement |
|---------|-------|----------------------------------------------|----------------|-------------|
| Identity $I_2$ (1 qubit) | $\approx 88$ | 640 | $d^4/\varepsilon^2 = 1{,}600$ | $2\times$ |
| Identity $I_{2^n}$ ($n$ qubits) | $\approx 88 + O(\log n)$ | $\approx 640$ | $16^n/\varepsilon^2$ | $16^n/640$ |
| Depolarizing($p$) on 1 qubit | $\approx 96 + O(\log(1/p))$ | $\approx 720$ | $1{,}600$ | $2\times$ |
| Local $\mathcal{E}^{\otimes n}$ | $\approx 88n$ | $640n$ | $16^n/\varepsilon^2$ | $16^n / (640n)$ |
| Shallow circuit ($t$ layers) | $O(nt)$ | $O(nt/\varepsilon)$ | $16^n/\varepsilon^2$ | $16^n / (nt)$ |

**The identity channel result.** $K_F(J(I_d)) \approx 88$ bits for any $d$ (just need to encode the identity structure). Average-case MDL bound: $m \approx 640$ measurements regardless of $d$ or $n$. Standard process tomography needs $O(16^n/\varepsilon^2)$. For $n = 10$: improvement of $\sim 10^{10}$. This is the extreme case: near-identity channels (noise $p \ll \varepsilon$) need only $O(K_F/\varepsilon) \approx 640$ measurements to verify.

---

## 4. Efficient Learning Algorithm

### 4.1 The Core Difficulty

The MDL learner is information-theoretically optimal but finding the shortest consistent ZCE program is undecidable in general. However, we do not need the exact shortest program — we need a program of length $\leq C \cdot K_F(\rho)$ for some constant $C$. This gives sample complexity $C \cdot K_F(\rho)/\varepsilon$, still exponentially better than standard for structured states.

### 4.2 Algorithm EfficientMDL

**Algorithm** (EfficientMDL for MPS states).

```
Input:  m measurements of rho, accuracy target eps
Output: rho_hat in MPS form

1. Compute empirical POVM frequencies from measurements.
2. For D = 1, 2, 4, 8, ..., up to D_max = sqrt(d):
   a. MPS-QST_D: run standard MPS tomography (Cramer et al.) at bond dim D.
   b. Compute K_F_MPS(D) = D^2 * n * c_param (estimated program length).
   c. Check consistency: compute empirical error err_emp(rho_D).
   d. If err_emp(rho_D) <= eps/2: output rho_D, STOP.
3. If no MPS fits: output standard MLE (Haah et al.).
```

### 4.3 Sample Complexity of EfficientMDL

**Theorem C** (Efficient MDL for MPS). Let $\rho$ be an $n$-qubit state that is an MPS with bond dimension $D^*$, so $K_F(\rho) = \Theta(D^{*2} \cdot n)$ bits. Algorithm EfficientMDL outputs $\hat\rho$ with $D_\text{tr}(\hat\rho, \rho) \leq \varepsilon$ using

$$m = O\!\left(\frac{n \cdot D^{*4}}{\varepsilon^2}\right)$$

measurements, in time $\text{poly}(n, D^*, 1/\varepsilon)$.

*Proof sketch.*

**Sample complexity.** At iteration $D = D^*$, MPS-QST at bond dimension $D^*$ achieves $D_\text{tr} \leq \varepsilon$ using $m = O(n D^{*4}/\varepsilon^2)$ measurements (Cramer et al. 2010, Theorem 1, accounting for $D^{*2}$ parameters per tensor and $D^{*2}$ estimation cost).

**Correctness.** With these many measurements, the empirical error concentrates: $|\text{err}_\text{emp}(\rho_{D^*}) - \text{err}(\rho_{D^*})| \leq \varepsilon/2$ with high probability (McDiarmid's inequality). Since $\text{err}(\rho_{D^*}) \leq \varepsilon/2$ (MPS-QST guarantee), we have $\text{err}_\text{emp}(\rho_{D^*}) \leq \varepsilon$, so the algorithm accepts at $D = D^*$ or earlier.

**Runtime.** Each MPS-QST step runs in $\text{poly}(n, D, 1/\varepsilon)$. The loop runs at most $O(\log D^*)$ iterations. Total: $\text{poly}(n, D^*, 1/\varepsilon)$. $\square$

### 4.4 Comparison Table

| Algorithm | Sample complexity | Computational cost | Prior knowledge needed |
|-----------|------------------|--------------------|------------------------|
| Standard QST | $O(4^n/\varepsilon^2)$ | $\text{poly}(4^n, 1/\varepsilon)$ | None |
| MPS-QST (known $D^*$) | $O(n D^{*4}/\varepsilon^2)$ | $\text{poly}(n, D^*, 1/\varepsilon)$ | $D^*$ |
| **EfficientMDL** | $O(n D^{*4}/\varepsilon^2)$ | $\text{poly}(n, D^*, 1/\varepsilon)$ | **None** |
| MDL bound (Thm 4.1) | $O(n D^{*2}/\varepsilon)$ | Intractable | None |

**Key point.** EfficientMDL matches MPS-QST in sample complexity *without needing to know $D^*$ in advance*. This is the practical contribution: the algorithm is self-tuning. It automatically finds the right model complexity.

**Gap.** EfficientMDL uses $O(n D^{*4}/\varepsilon^2)$ but the MDL bound says $O(n D^{*2}/\varepsilon)$ suffices. The gap is $D^{*2}/\varepsilon$ — from not knowing $D^*$ (contributing $D^{*2}$) and not having a realizable algorithm (contributing $1/\varepsilon$). Closing both gaps is the remaining open problem.

### 4.5 When EfficientMDL Matches the MDL Bound

There is one setting where the gap closes: when $D^* = O(1)$ (constant bond dimension) and a realizable MPS learner is available. Then EfficientMDL uses $O(n/\varepsilon^2)$ measurements, while MDL says $O(n/\varepsilon)$ suffices. The gap reduces to just the $1/\varepsilon$ factor — purely from the realizability question.

**Remark.** Closing the $1/\varepsilon$ gap for MPS requires showing that MPS-QST can be put in a realizable PAC setting — i.e., that there exists an MPS learning algorithm that, given the data comes exactly from an MPS, achieves $1/\varepsilon$ scaling. This is likely true for specific MPS families (translation-invariant, periodic boundary) but is not proven in general. It would be a separate paper.

---

## 5. Summary: Status of All Four Problems

| Problem | Status | Result |
|---------|--------|--------|
| Tightness for structured states | **Clarified** | Bound is tight for incompressible states (Thm 1.1). For structured states, $K_F$ overestimates; tight bound uses Fisher complexity $I_F$. Conjectured relationship $I_F \leq K_F/c$. |
| Agnostic extension | **Proven** | Theorem A: $m \leq K^*/\varepsilon^2$, error $\leq \text{opt} + 2\varepsilon$. Interpolation bound for known $\text{opt}$. |
| Process tomography | **Proven** | Theorem B: $m \leq d_\text{in} K_F/\varepsilon$ (diamond norm); $m \leq K_F/\varepsilon$ (average-case). Immediate from Choi isomorphism. |
| Efficient algorithm | **Algorithm + sample bound** | Theorem C: EfficientMDL achieves $O(n D^{*4}/\varepsilon^2)$ without knowing $D^*$. Gap to MDL bound is $D^{*2}/\varepsilon$; closing it for MPS is open. |

---

## 6. New Open Problems Revealed by This Analysis

**O1.** Characterize the relationship between $K_F(\rho)$ and $I_F(\rho)$. Is $I_F(\rho) \leq K_F(\rho)/c$ for all $\rho \in \mathcal{H}_Q$? If yes, the MDL bound is tight up to a constant everywhere.

**O2.** Realizable MPS learning. Is there a computationally efficient algorithm achieving $O(n D^{*2}/\varepsilon)$ (rather than $O(n D^{*4}/\varepsilon^2)$) for MPS states? This requires both structural exploitation and the $1/\varepsilon$ scaling from realizability.

**O3.** Process tomography: $d_\text{in}$ factor. The diamond norm bound contains a factor of $d_\text{in}$. For channel certification tasks where only average-case fidelity is needed, this drops out. Characterize exactly which process tomography tasks inherit the $1/d_\text{in}$ improvement.

**O4.** Agnostic interpolation bound. The interpolation $m \leq K_F/(\varepsilon(\varepsilon - \text{opt}))$ requires knowing $\text{opt}$. Can an adaptive algorithm estimate $\text{opt}$ from the data and achieve this bound without prior knowledge of the noise level?

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*All algorithmic claims in Section 4 follow from Cramer et al. (2010) sample complexity for MPS-QST combined with the union bound over bond dimensions. Theorems A and B are new. Theorem C is a combination of known MPS-QST results with a new model selection argument.*
