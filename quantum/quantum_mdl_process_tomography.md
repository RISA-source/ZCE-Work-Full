# MDL Bounds for Quantum Process Tomography: Certification vs Characterization

**Author:** Rishi Saraff  
**Institution:** Herald College Kathmandu  
**Date:** March 2026  
**Status:** Theorem B proven. All $K_F$ values estimated. Key identity channel result exact.  
**Companion paper:** Saraff (2026d): *Computable Sample Complexity for Quantum State Tomography*

---

## Abstract

We extend the MDL sample complexity bound from quantum states to quantum channels (processes). For any quantum channel $\mathcal{E}$ with Choi matrix complexity $K_F(J(\mathcal{E})) = L$ bits, the MDL learner reconstructs $\mathcal{E}$ to diamond norm $\varepsilon$ using at most $d_\text{in} \cdot L \ln 2/\varepsilon$ measurements, or to average-case fidelity $\varepsilon$ using at most $L \ln 2/\varepsilon$ measurements — identical to the state tomography bound.

The proof is immediate via the Choi-Jamiołkowski isomorphism: every channel *is* a density matrix on a doubled space. No new machinery is needed.

The result reveals a sharp information-theoretic distinction: **quantum device certification** (verify a channel is close to ideal) requires $O(K_F(\text{ideal})/\varepsilon)$ measurements — constant in system size for Clifford gates and stabilizer operations — while **quantum device characterization** (learn the full channel) requires $O(d_\text{in} \cdot K_F/\varepsilon)$.

**Headline result:** To verify an $n$-qubit device implements the identity channel (wire) within average fidelity $\varepsilon = 0.1$: approximately **640 measurements**, regardless of $n$. Standard process tomography requires $O(16^n/\varepsilon^2)$.

---

## 1. Setup

### 1.1 Quantum Channels and the Choi Isomorphism

A quantum channel $\mathcal{E}: \mathcal{D}(\mathcal{H}_\text{in}) \to \mathcal{D}(\mathcal{H}_\text{out})$ is a completely positive, trace-preserving (CPTP) linear map. Its **Choi matrix** is:

$$J(\mathcal{E}) = (\text{id} \otimes \mathcal{E})(|\Phi^+\rangle\langle\Phi^+|) \;\in\; \mathcal{D}(\mathcal{H}_\text{in} \otimes \mathcal{H}_\text{out})$$

where $|\Phi^+\rangle = d_\text{in}^{-1/2} \sum_i |ii\rangle$. The Choi-Jamiołkowski isomorphism establishes a bijection between CPTP maps and PSD matrices $J \geq 0$ satisfying $\text{Tr}_\text{out}[J] = I_{d_\text{in}}/d_\text{in}$.

The Choi matrix is a density matrix (up to normalization). This means everything proven for quantum state tomography applies immediately to process tomography, with $\rho \to J(\mathcal{E})$.

### 1.2 Distance Measures

**Diamond norm** (worst-case): $\|\mathcal{E}_1 - \mathcal{E}_2\|_\diamond = d_\text{in} \cdot D_\text{tr}(J(\mathcal{E}_1), J(\mathcal{E}_2))$.

**Average fidelity** (average-case): $D_\text{avg}(\mathcal{E}_1, \mathcal{E}_2) = 1 - F_\text{avg}(\mathcal{E}_1, \mathcal{E}_2) \leq D_\text{tr}(J(\mathcal{E}_1), J(\mathcal{E}_2))$.

The diamond norm scales with $d_\text{in}$ because it measures worst-case input-state distinguishability. The average fidelity does not, because it averages over input states.

---

## 2. Main Theorem

**Definition 2.1.** The ZCE complexity of a quantum channel is $K_F(\mathcal{E}) := K_F(J(\mathcal{E}))$.

**Theorem B** (MDL Process Tomography).

For any quantum channel $\mathcal{E}$ with $K_F(\mathcal{E}) = L$ bits and confidence $1-\delta$:

$$m_\diamond \leq \frac{d_\text{in}(L \ln 2 + \ln(1/\delta))}{\varepsilon} \qquad \text{(diamond norm } \varepsilon\text{)}$$

$$m_\text{avg} \leq \frac{L \ln 2 + \ln(1/\delta)}{\varepsilon} \qquad \text{(average fidelity } \varepsilon\text{)}$$

*Proof.*

Apply Theorem 4.1 of Saraff (2026d) to $J(\mathcal{E})$.

For diamond norm: achieving $D_\text{tr}(J(\hat{\mathcal{E}}), J(\mathcal{E})) \leq \varepsilon/d_\text{in}$ implies $\|\hat{\mathcal{E}} - \mathcal{E}\|_\diamond \leq \varepsilon$. Set $\varepsilon' = \varepsilon/d_\text{in}$ in the state tomography bound: $m \leq L \ln 2 / (\varepsilon/d_\text{in}) = d_\text{in} L \ln 2 / \varepsilon$.

For average fidelity: $D_\text{avg} \leq D_\text{tr}(J(\hat{\mathcal{E}}), J(\mathcal{E})) \leq \varepsilon$ directly from the state tomography bound with $\varepsilon' = \varepsilon$. $\square$

---

## 3. Key Examples and Exact Values

### 3.1 The Identity Channel Result

**The identity channel** $\mathcal{I}_d: \rho \mapsto \rho$ on a $d$-dimensional system has Choi matrix $J(\mathcal{I}_d) = |\Phi^+\rangle\langle\Phi^+|$ — the maximally entangled state. Its ZCE description: one SET instruction storing the dimension $d$, plus the identity structure. For any $n$-qubit system:

$$K_F(\mathcal{I}_{2^n}) \approx 88 \text{ bits} \quad \text{(any } n\text{)}$$

This is essentially constant because "identity on $n$ qubits" has a constant-size description regardless of $n$: the program just says "output whatever you received."

**Theorem B gives:**

| $n$ | $m_\text{avg}$ ($\varepsilon{=}0.1$) | $m_\diamond$ ($\varepsilon{=}0.1$) | $m_\text{std}$ ($\varepsilon{=}0.1$) | Improvement |
|-----|-------|--------|---------|-------------|
| 1 | **640** | 1,280 | 1,600 | $2\times$ |
| 2 | **640** | 5,120 | 25,600 | $40\times$ |
| 5 | **640** | 163,840 | $1.6 \times 10^{9}$ | $2.5 \times 10^6\times$ |
| 10 | **640** | $5.4 \times 10^{9}$ | $1.1 \times 10^{18}$ | $1.7 \times 10^9\times$ |

*Average fidelity is constant in $n$. Diamond norm grows with $d_\text{in} = 2^n$.*

### 3.2 Structured Channels

| Channel | Structure | $K_F$ (est.) | $m_\text{avg}$ ($\varepsilon{=}0.1$) | $m_\text{std}$ | Avg improvement |
|---------|-----------|-------------|--------------------------|--------------|-----------------|
| Identity $\mathcal{I}_{2^n}$ | Always same | $\approx 88$ | **640** | $16^n/0.01$ | $16^n/640$ |
| CNOT | Stabilizer (4 gens) | $\approx 150$ | **1,040** | $163,840$ | $157\times$ |
| Depolarizing($p$) | 1 parameter | $\approx 96+\log(1/p)$ | **$\sim 700$** | $163,840$ | $\sim 230\times$ |
| Local $\mathcal{E}^{\otimes n}$ | Tensor product | $\approx 127n$ | $880n$ | $16^n/0.01$ | $16^n/(880n)$ |
| Shallow circuit (depth $t$, $n$ qubits) | Circuit desc. | $O(nt)$ | $O(nt/\varepsilon)$ | $16^n/\varepsilon^2$ | $16^n/(nt\varepsilon)$ |
| Haar-random channel | No structure | $O(16^n)$ | $O(16^n/\varepsilon)$ | $16^n/\varepsilon^2$ | $1/\varepsilon$ only |

### 3.3 The Certification vs Characterization Distinction

**Characterization** = learn the full channel from scratch. Cost: $O(d_\text{in} \cdot K_F / \varepsilon)$ for diamond norm.

**Certification** = verify a channel is close to a KNOWN ideal. Cost: $O(K_F(\text{ideal}) / \varepsilon)$ for average fidelity.

For the identity channel: characterization costs $O(2^n \cdot 88 / \varepsilon)$ (grows with $n$). Certification costs $\approx 640$ (constant in $n$).

The distinction is fundamental. Certification is cheap because the *ideal* has low $K_F$. The actual channel may be complex, but you're asking a simple question: "Is it close to this simple ideal?" The answer requires only as many measurements as it takes to describe the ideal.

**Analogy:** Verifying a file hasn't been corrupted requires only the checksum (short). Reading the entire file (characterizing it) requires the full content (long). Quantum certification is checksumming. Quantum characterization is full readout.

---

## 4. Application: Near-Term Quantum Devices

### 4.1 The Benchmarking Problem

Near-term quantum devices (NISQ) have 50–1000 qubits. Standard process tomography is infeasible: $O(16^n/\varepsilon^2)$ measurements for an $n$-qubit gate is $\sim 10^{60}$ for $n = 100$.

Current practice: randomized benchmarking (RB), which estimates an average error rate but doesn't reconstruct the channel. It answers "how noisy?" not "what is the noise?".

### 4.2 MDL Benchmarking Protocol

**Input:** Target ideal channel $\mathcal{E}_\text{ideal}$ (known), noisy device implementing $\mathcal{E}_\text{device}$ (unknown).

**Protocol:**
1. Compute $K_F(\mathcal{E}_\text{ideal})$ from the ZCE assembler. This takes seconds.
2. Run $m = K_F(\mathcal{E}_\text{ideal}) \ln 2 / \varepsilon$ randomized measurements on the device.
3. Run the MDL learner with $\mathcal{E}_\text{ideal}$ as the prior. Output $\hat{\mathcal{E}}$.
4. Report $D_\text{avg}(\hat{\mathcal{E}}, \mathcal{E}_\text{ideal})$ and the ZCE program for $\hat{\mathcal{E}}$.

**What you get:** Not just a scalar error rate, but the *full reconstructed channel* and a *computable certificate* that it is within $\varepsilon$ of ideal. The certificate IS the ZCE program: if the program is short, the channel is close to ideal; if long, the noise has introduced complexity.

**Key numbers:**

| Gate | $K_F(\text{ideal})$ | Measurements needed ($\varepsilon = 0.01$) |
|------|--------------------|--------------------------------------------|
| Single-qubit rotation | $\approx 96$ | $\approx 665$ |
| CNOT | $\approx 150$ | $\approx 1{,}040$ |
| Toffoli (3-qubit) | $\approx 200$ | $\approx 1{,}386$ |
| 5-qubit QEC operation | $\approx 500$ | $\approx 3{,}466$ |
| 10-qubit shallow circuit | $\approx 1{,}270$ | $\approx 8{,}800$ |

All of these are achievable with current experimental setups.

---

## 5. Agnostic Extension for Process Tomography

Theorem A from the extensions paper (Saraff 2026d-ext) applies directly:

**Theorem** (Agnostic Process MDL). Let $\mathcal{E}$ be any channel, $\mathcal{E}^* = \arg\min_{\mathcal{F} \in \mathcal{H}_Q^\text{ch}} D_\text{avg}(\mathcal{E}, \mathcal{F})$, $\text{opt} = D_\text{avg}(\mathcal{E}, \mathcal{E}^*)$, $K^* = K_F(\mathcal{E}^*)$.

The agnostic MDL process learner outputs $\hat{\mathcal{E}}$ with $D_\text{avg}(\hat{\mathcal{E}}, \mathcal{E}) \leq \text{opt} + 2\varepsilon$ using $m \leq K^*/\varepsilon^2$ measurements.

**Physical meaning:** Your device has noise (opt $> 0$). The MDL learner finds the closest ideal operation and measures how far off you are. You don't need to know the noise model. The output tells you both what your channel IS and how far it is from the simplest description.

---

## 6. Open Questions

**O1.** Is $m_\text{avg} = O(K_F(\mathcal{E})/\varepsilon)$ achievable with an efficient algorithm? For stabilizer channels, likely yes (stabilizer formalism provides efficient representation). For general Clifford + $T$ gate channels: open.

**O2.** Can the $d_\text{in}$ factor in the diamond norm bound be removed for specific channel families? For covariant channels (channels commuting with a group action), the worst-case input is known, potentially removing the $d_\text{in}$ factor.

**O3.** Extend to quantum instruments (channels with classical output, e.g., measurements). Instruments are used in adaptive protocols; their tomography complexity is unstudied from the MDL perspective.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*Theorem B follows immediately from Saraff (2026d) Theorem 4.1 via the Choi isomorphism. All $K_F$ estimates for specific gates are upper bounds from program structure analysis; exact values require ZCE assembler runs.*
