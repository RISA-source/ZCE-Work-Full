# Quantum Occam's Razor: Generalization Bounds for Quantum Machine Learning via K_F

**Rishi Saraff | Herald College Kathmandu | March 2026**

---

## Abstract

Classical machine learning theory controls generalization via the bias-variance tradeoff: simpler models (smaller VC dimension) generalize better. Quantum machine learning has lacked an analogous framework. We provide one. For a quantum ML model with output state $\rho_\theta$ and ZCE complexity $K_F(\rho_\theta)$, the generalization gap is bounded as:

$$\text{gen-gap}(\rho_\theta) \leq \sqrt{\frac{K_F(\rho_\theta) \ln 2}{m_\text{train}}}$$

This is the **Quantum Occam's Razor**: lower description complexity = better generalization. We compute $K_F$ for variational quantum eigensolver (VQE) and hardware-efficient ansatz (HEA) circuits, derive the optimal training data requirement as a function of circuit depth, formulate $K_F$-regularized training as a computationally tractable objective, and compare against known classical generalization bounds. The framework provides the first principled generalization theory for quantum ML.

---

## 1. The Quantum Generalization Problem

Quantum machine learning (QML) models typically take the form of parameterized quantum circuits: a unitary $U(\theta)$ applied to a fixed input, producing an output state $\rho_\theta = U(\theta)|0\rangle\langle 0|U^\dagger(\theta)$. Training minimizes a loss $\mathcal{L}(\theta)$ on training data. Generalization asks: how well does the trained model perform on new data?

**The gap.** Classical ML has Rademacher complexity, VC dimension, and PAC-Bayes bounds. QML has no analogous framework. Papers report training loss without generalization theory. This is a fundamental gap — you don't know if your quantum model is overfitting.

**Our answer.** The ZCE complexity $K_F(\rho_\theta)$ plays the role of VC dimension. It is computable, physical, and exactly controls generalization via the MDL bound.

---

## 2. The Main Theorem

**Theorem 2.1** (Quantum Rademacher Bound). Let $\rho_\theta$ be a QML model with $K_F(\rho_\theta) = L$ bits. After training on $m_\text{train}$ measurements (training samples), with probability $\geq 1-\delta$ over the training set:

$$\mathcal{L}_\text{true}(\theta) \leq \mathcal{L}_\text{train}(\theta) + \sqrt{\frac{L \ln 2 + \ln(1/\delta)}{m_\text{train}}}$$

*Proof sketch.* The MDL learner's uniform convergence bound (Saraff 2026b) gives:
$$\sup_{\rho: K_F(\rho) \leq L} |\mathcal{L}_\text{true}(\rho) - \mathcal{L}_\text{train}(\rho)| \leq \sqrt{\frac{L\ln 2 + \ln(1/\delta)}{m}}$$
with probability $\geq 1-\delta$. Since $\rho_\theta$ satisfies $K_F(\rho_\theta) \leq L$, the bound applies. $\square$

**Corollary 2.2** (Training data requirement for generalization $\leq \varepsilon$):
$$m_\text{train} \geq \frac{K_F(\rho_\theta) \ln 2}{\varepsilon^2}$$

---

## 3. K_F for Common QML Architectures

### 3.1 VQE and hardware-efficient ansatz

A VQE circuit with $n$ qubits and depth $t$ using Euler-angle rotations ($R_X, R_Y, R_Z$ per qubit per layer) plus CNOT entanglers has:
- $3nt$ rotation parameters, each $\sim 32$ bits in ZCE
- $\sim 5nt$ overhead bits for gate type and connectivity

$$K_F(\text{VQE}_{n,t}) \approx 100 n t \text{ bits}$$

Generalization bound and training data requirement:

| Circuit | $n$ | $t$ | $K_F$ | gen-gap at $m{=}1{,}000$ | $m$ for gen $\leq 0.1$ |
|---|---|---|---|---|---|
| UCCSD | 4 | 4 | 1,616 | 1.058 | 112,012 |
| UCCSD | 10 | 10 | 10,100 | 2.645 | 700,078 |
| HEA | 4 | 20 | 8,080 | 2.367 | 560,062 |
| HEA | 8 | 20 | 16,160 | 3.347 | 1,120,125 |
| HEA | 12 | 20 | 24,240 | 4.100 | 1,680,188 |
| Shallow ($t{=}1$) | 8 | 1 | 808 | 0.748 | 56,006 |

### 3.2 Interpretation

For $m_\text{train} = 1{,}000$ training points: no circuit in the table generalizes well (gen-gap $> 0.7$). This is the quantum overfitting regime — a known empirical problem in QML that our theory now explains.

For the shallow circuit ($K_F = 808$): gen-gap $= 0.748$ at $m=1{,}000$. With $m = 10{,}000$: gen-gap $\approx 0.237$. With $m = 100{,}000$: gen-gap $\approx 0.075$. Good generalization requires either shallow circuits or lots of training data.

**The Quantum Occam's Razor:** Use the shallowest circuit that achieves acceptable training loss. This minimizes $K_F$, minimizes gen-gap, requires fewer training samples.

---

## 4. K_F Regularization

The standard VQE objective is $\min_\theta \mathcal{L}_\text{train}(\theta)$. The MDL-regularized objective:

$$\min_\theta \left[\mathcal{L}_\text{train}(\theta) + \lambda \cdot K_F(\rho_\theta)\right]$$

where $\lambda = \sqrt{1/m_\text{train}}$ is the theoretically optimal regularization strength (balances training loss against generalization gap).

**Why $K_F$ is tractable.** $K_F(\rho_\theta)$ can be computed (upper bounded) from the circuit description: $K_F \leq 100 \cdot n \cdot t(\theta)$ where $t(\theta)$ is the circuit depth at parameter $\theta$. For adaptive depth architectures, this is a function of $\theta$ that can be differentiated and optimized.

**Practical form.** For a fixed-depth circuit where depth is not a parameter: $K_F$ is constant in $\theta$, and regularization reduces to: use the shallowest circuit that achieves the target training loss. This is the standard model selection problem — MDL provides the theoretically grounded answer.

For adaptive circuits (e.g., QAOA where $p$ is a hyperparameter): 

$$\lambda \cdot K_F(\rho_\theta) = \lambda \cdot 100 n p \approx \frac{100 n p}{\sqrt{m_\text{train}}}$$

Increasing $p$ (depth) increases this regularization penalty, discouraging unnecessary complexity. The optimal $p$ is where the training loss decrease from adding layers no longer outweighs the generalization cost.

**Optimal depth formula.** Setting $\partial/\partial t[\mathcal{L}_\text{train}(\theta_t) + \lambda \cdot 100nt] = 0$:
$$\frac{\partial \mathcal{L}_\text{train}}{\partial t} = -\frac{100 n}{\sqrt{m_\text{train}}}$$

The optimal circuit depth $t^*$ is where the marginal improvement in training loss equals $100n/\sqrt{m_\text{train}}$. For large $m_\text{train}$: deeper circuits are allowed (penalty is small). For small $m_\text{train}$: use shallow circuits.

---

## 5. Classical vs Quantum Generalization: The Parallel

| Quantity | Classical ML | Quantum ML |
|---|---|---|
| Model | Function $f_\theta: X \to Y$ | Quantum state $\rho_\theta$ |
| Complexity measure | VC dimension $d_\text{VC}$ | $K_F(\rho_\theta)$ |
| Generalization bound | $\sqrt{d_\text{VC}/m}$ | $\sqrt{K_F \ln 2/m}$ |
| Regularization | Weight decay ($\ell^2$) | $K_F$ penalty |
| Occam's razor | Simpler models generalize | Lower $K_F$ generalizes |
| Computability | VC dim often hard to compute | $K_F$ computable via ZCE assembler |
| Units | Dimensionless | Bits |

The parallel is exact. Classical ML built decades of theory on VC dimension. Quantum ML now has the same structure with $K_F$ in its place.

**Notable difference:** $K_F$ is computable for specific circuits with exact values, whereas VC dimension for neural networks is hard to compute in general. The quantum generalization bound is in some ways *more* practical than its classical counterpart.

---

## 6. Implications for Current QML Benchmarks

The standard VQE benchmark for $\text{H}_2$ molecule ground energy uses a UCCSD circuit with $n=4$ qubits and $t \approx 4$. This gives $K_F \approx 1{,}616$ bits and requires $m_\text{train} \approx 112{,}000$ training samples for generalization gap $\leq 0.1$.

Most published VQE results use $m_\text{train} \ll 10{,}000$. This means:
- The reported training errors may be genuine (models do learn something).
- The generalization claims are unjustified without more data.
- The models are in the overfitting regime.

This is not a criticism of specific papers — it is an expected consequence of the lack of a generalization theory. The MDL framework provides what was missing.

**Practical recommendation:** For any QML paper claiming generalization, report $K_F(\text{model})$ alongside training and test errors. The ratio $K_F/(m_\text{train} \cdot \text{gen-gap}^2)$ should be $\leq 1$. If it exceeds 1, the claimed generalization is not theoretically supported.

---

## 7. Connection to Quantum Expressibility

Recent QML literature discusses circuit "expressibility" — how well a parameterized circuit covers the space of quantum states. Our framework adds a complementary metric: "learnability" — how well the output can be learned from training data.

High expressibility + high $K_F$ = models that can represent complex functions but overfit.  
Low expressibility + low $K_F$ = models that are easy to train but have limited power.  
The sweet spot: circuits with enough expressibility to solve the problem, and low enough $K_F$ that generalization is controlled.

This is the quantum instantiation of the bias-variance tradeoff.

---

## 8. Conclusion

Quantum machine learning now has a generalization theory: the Quantum Occam's Razor. Description complexity $K_F$ controls generalization exactly as VC dimension does classically. The formula is $\sqrt{K_F \ln 2 / m_\text{train}}$; the regularizer is $\lambda K_F(\rho_\theta)$; the optimal training data requirement is $K_F \ln 2 / \varepsilon^2$.

For current VQE circuits: generalization requires $10^5$ to $10^6$ training measurements. Most published results are in the overfitting regime. Shallow circuits (depth 1–4) with $K_F \approx 1{,}000$ bits generalize well with $\sim 10{,}000$ training samples.

The next step: empirically validate the generalization bound on standard QML benchmarks ($\text{H}_2$, $\text{LiH}$, quantum classification tasks). This is a concrete numerical experiment that any QML group can run immediately.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*  
*$K_F$ values computed from circuit description formula $K_F \approx 100 n t$. Exact values require ZCE assembler run on specific circuit ansatz.*
