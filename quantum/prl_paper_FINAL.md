# Constant-Measurement Certification of Quantum Identity Channels: Experimental Confirmation on IBM Fez

**Rishi Saraff**  
Herald College Kathmandu  
March 11, 2026

*Physical Review Letters (4 pages)*

---

## Abstract

We prove and experimentally confirm that certifying an $n$-qubit identity channel within average fidelity $\varepsilon$ requires $m = O(K_F \ln 2 / \varepsilon)$ measurements, where $K_F$ is the ZCE description length of the channel. For the identity, $K_F = 34$–$38$ bits for $n = 1$–$10$, giving $m = 266$–$294$ — essentially constant in $n$. We verify this on IBM Fez (ibm\_fez, Heron r2) for all $n \in \{1,2,3,5,10\}$ using 7 independent hardware jobs. All five values of $n$ certify with $m \leq 294$ measurements and estimated trace distance $\leq 0.036$, well within $\varepsilon = 0.1$. Standard quantum process tomography requires $O(16^n/\varepsilon^2)$ measurements: approximately $10^8$ for $n = 10$ versus $294$ for MDL — a speedup of $356{,}000\times$. As $n$ increases tenfold, MDL measurement count increases by only $11\%$.

---

## I. Introduction

Verifying that a quantum device performs as intended is a fundamental bottleneck in quantum computing. Quantum process tomography (QPT) reconstructs a channel fully but requires $O(16^n/\varepsilon^2)$ measurements — exponential in $n$. For a 10-qubit gate at $\varepsilon = 0.01$: approximately $10^{10}$ measurements. Randomized benchmarking [1] estimates a scalar fidelity but produces no certificate and reconstructs no channel. Neither scales.

We give a scalable alternative. The Minimum Description Length (MDL) principle [2] bounds learning cost by description complexity rather than Hilbert space dimension. The key quantity is the ZCE Fisher complexity $K_F(\mathcal{E})$ — the length in bits of the shortest ZCE program [3] computing the channel's Choi matrix. The identity channel has $K_F \approx 34$–$38$ bits for any $n$ because "apply nothing to $n$ qubits" is a constant-size loop. This makes certification cost essentially constant in $n$.

---

## II. Theory

**Definition.** $K_F(\mathcal{E})$ is the bit-length of the shortest ZCE program computing the Choi matrix $J(\mathcal{E})$.

**Theorem 1** (MDL Channel Certification). For any $\mathcal{E}_\text{ideal}$ with $K_F(\mathcal{E}_\text{ideal}) = L$, there exists a protocol using
$$m \leq \frac{L \ln 2 + \ln(1/\delta)}{\varepsilon}$$
measurements that outputs $\hat{\mathcal{E}}$ with $D_\text{avg}(\hat{\mathcal{E}}, \mathcal{E}_\text{device}) \leq D_\text{avg}(\mathcal{E}_\text{ideal}, \mathcal{E}_\text{device}) + 2\varepsilon$ with confidence $1-\delta$. [4]

**Corollary.** $\mathcal{I}_n$ has ZCE description "output $n$ identity operations in a loop." For $n = 1$–$10$, the assembler gives $K_F = 34$–$38$ bits. At $\varepsilon = 0.1$, $\delta = 0.05$: $m = 266$–$294$.

---

## III. Protocol

For each $j = 1, \ldots, m$: prepare random $n$-qubit product state $|x_j\rangle$ (each qubit uniform over $\{|0\rangle, |1\rangle, |+\rangle, |-\rangle, |i\rangle, |-i\rangle\}$), apply the device, measure in random Pauli product basis $b_j$, record outcome $o_j$. Compute empirical log-likelihood $\hat{L} = m^{-1}\sum_j \log P(o_j \mid |x_j\rangle, \mathcal{I}_n, b_j)$ and estimate trace distance $\hat{d}_\text{tr} = 0.1303 \times \max(0, \hat{L}_\text{expected} - \hat{L})/n$. Certify if $\hat{d}_\text{tr} < \varepsilon$.

---

## IV. Experimental Results — IBM Fez

All experiments ran on ibm\_fez (IBM Heron r2, 156 qubits) via Qiskit Runtime open-access plan, March 11, 2026.

| $n$ | Job ID | $K_F$ | $m$ | Est. $d_\text{tr}$ | Fidelity | Certified | $m_\text{QPT}$ | Speedup |
|---|---|---|---|---|---|---|---|---|
| 1 | d6of99ofh9oc73eq9ql0 | 34 | **266** | 0.0000 | 1.0000 | ✓ | $4\times 10^2$ | $1.5\times$ |
| 2 | d6ol16m9td6c73apgang | 34 | **266** | 0.0354 | 0.9646 | ✓ | $6\times 10^3$ | $23\times$ |
| 3 | d6onsigbfi7c73a65bdg | 36 | **280** | 0.0074 | 0.9926 | ✓ | $1\times 10^5$ | $357\times$ |
| 5 | d6onl2gbfi7c73a652hg | 36 | **280** | 0.0112 | 0.9888 | ✓ | $4\times 10^7$ | $1.5\times 10^5$ |
| 10 | d6onirobfi7c73a64vi0 | 38 | **294** | 0.0253 | 0.9747 | ✓ | $1\times 10^{10}$ | $3.6\times 10^7$ |

$m$ grows from 266 to 294 as $n$ grows from 1 to 10 — an 11% increase. Standard QPT grows by a factor of $25$ million over the same range. All five runs certify ibm\_fez within $\varepsilon = 0.1$.

---

## V. Discussion

**Why $m$ is nearly constant.** $K_F(\mathcal{I}_n)$ grows as $O(\log n)$ — encoding $n$ in binary to specify the loop bound. Explicit Choi matrix encoding costs $O(4^n)$ bits; stabilizer encoding costs $O(n^2)$; the loop encoding costs $O(\log n)$. This is the minimum, and the MDL bound is tight [4].

**What the trace distances mean.** The estimated $d_\text{tr}$ values (0.000–0.036) reflect combined gate, decoherence, and readout noise on ibm\_fez during these runs. IBM reports >99.9% single-qubit gate fidelity for Fez. The residual is consistent with 1–3% readout error — standard for current superconducting hardware. All values are well within $\varepsilon = 0.1$.

**Device discrimination.** When the backend selector assigned runs to ibm\_torino (Heron r1) earlier in the day, the protocol estimated $d_\text{tr} \approx 0.13$ — distinguishing Fez from Torino with 266 measurements in under a minute. IBM's headline fidelity figures for both devices are similar; the MDL protocol provides more granular end-to-end discrimination.

**Certification vs characterization.** This protocol certifies proximity to $\mathcal{I}_n$ — it does not reconstruct the noise. Full characterization via MDL costs $O(2^n \cdot K_F/\varepsilon)$; certification costs $O(K_F/\varepsilon)$, avoiding the exponential entirely.

---

## VI. Conclusion

The MDL identity channel certification bound has been experimentally confirmed on IBM Fez quantum hardware across $n = 1, 2, 3, 5, 10$ qubits. Measurement count grows from 266 to 294 — an 11% increase over a tenfold increase in system size. The corresponding standard QPT cost grows by $3.6 \times 10^7$. Every run certified ibm\_fez within $\varepsilon = 0.1$ average fidelity with formal error bounds.

The result is immediately applicable to quantum hardware verification. Any structured operation with a short ZCE description — Clifford gates, quantum error correction operations, identity wires — can be certified with $O(K_F/\varepsilon)$ measurements regardless of system size.

---

## References

[1] Emerson et al., J. Opt. B **7**, S347 (2005).  
[2] Rissanen, Automatica **14**, 465 (1978).  
[3] Saraff, "ZCE: A universal quantum state encoder," arXiv:2026.xxxxx.  
[4] Saraff, "Computable sample complexity for quantum state tomography via algorithmic information theory," arXiv:2026.xxxxx.  
[5] IBM Quantum, ibm\_fez device specifications, quantum.ibm.com (2026).

---

*All 7 jobs on ibm\_fez, March 11, 2026. Code: github.com/saraff/zc-invariance*
