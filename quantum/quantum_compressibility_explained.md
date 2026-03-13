# Physical Reality Is Algorithmically Compressible
## What the Claim Actually Means, Layer by Layer

**Rishi Saraff | March 2026**

---

## The Claim

> *Physical reality is algorithmically compressible. Quantum states that occur in nature have short descriptions. Laws of physics are short programs. Science is the process of finding minimum-description-length programs for observed data.*

This sounds like a philosophical slogan. It is not. It has three layers, and each layer has a different status — one is a proven theorem, one is a measured empirical fact, and one is a genuine unsolved question that predates quantum mechanics. Let's go through them in order.

---

## Layer 1: The Theorem (What Is Proven)

**Theorem.** If a quantum state $\rho$ has ZCE description length $K_F(\rho) = L$ bits, then the number of measurements needed to learn it is:
$$m^*(\rho, \varepsilon) = \Theta\!\left(\frac{L}{\varepsilon}\right)$$

This is the result proven in Saraff (2026d,f). It is tight. It connects two numbers that come from completely different places — how long it takes to *write down* a state, and how many measurements it takes to *learn* it — and says they are the same thing.

**What this says about compressibility:** If $L$ is small (state is compressible), then learning is cheap. If $L$ is large (state is incompressible), learning is expensive. Compressibility and learnability are exactly the same thing, measured in the same units.

This is not metaphor. It is a theorem with a proof. The compression ratio directly equals the measurement reduction. A state that is $10^{57}$ times more compressible than a random state requires $10^{57}$ fewer measurements to learn. That ratio is not abstract — it is the difference between "feasible in a laboratory" and "requires more time than the age of the universe."

---

## Layer 2: The Empirical Fact (What Is Measured)

**The observation:** Physical quantum states — ground states of local Hamiltonians, outputs of quantum circuits, thermal states, anything arising from a physical process — have $K_F$ that is exponentially smaller than random.

| State type | $K_F$ (100 qubits) | Measurements needed ($\varepsilon = 0.1$) |
|---|---|---|
| Haar-random state | $\sim 10^{62}$ bits | $\sim 10^{62}$ measurements |
| Ground state (area law) | $\sim 22{,}000$ bits | $\sim 150{,}000$ measurements |
| Depth-10 quantum circuit | $\sim 40{,}000$ bits | $\sim 280{,}000$ measurements |
| Product state | $\sim 12{,}700$ bits | $\sim 88{,}000$ measurements |

The compression ratio is $10^{57}$. That number needs to sit in your head for a moment.

A random 100-qubit state would require $10^{62}$ bits to describe. The ground state of a 100-atom Heisenberg chain — a real, physical object you can make in a cold atom lab — requires $22{,}000$ bits. Those two numbers differ by a factor of $10^{57}$. This is not a small correction. The universe is not *slightly* organized. It is organized to a degree that makes the word "organized" feel inadequate.

**Where does the compression come from?** This is provable (not just observed) for quantum circuits:

$$K_F(\rho_\text{circuit}) \leq K_F(\text{circuit description}) + O(n \log t)$$

A circuit with $n$ qubits, depth $t$, and $c$ bits per gate has complexity $\leq n \cdot t \cdot c$. The *output state* inherits this bound. If the circuit is short, the state is compressible. This is a theorem — the simulation theorem for ZCE programs. It says: the complexity of a quantum state is bounded by the complexity of the process that made it.

For physical states this chain is:
$$K_F(\text{physical state}) \leq K_F(\text{physical law}) + K_F(\text{dynamics}) + O(\text{overhead})$$

If the laws of physics are short programs (which is empirically true — more on this in Layer 3), then the states they produce are compressible. The compression of physical states follows directly from the compression of physical laws. The theorem makes this precise.

**The empirical part:** The claim "physical Hamiltonians are local" — meaning they only couple nearby sites — is an *observed* property of our universe, not a derived one. The Heisenberg model, the Hubbard model, QED, the entire Standard Model: all are local field theories. $K_F(\text{local Hamiltonian on } n \text{ sites}) = O(n)$. This is measured, not proven from first principles.

**What this means for experiment:** Cold atom experiments currently measure $\sim 10{,}000$ sites per run. A 100-site 1D chain has $K_F \approx 22{,}000$ bits. MDL learning requires $\sim 150{,}000$ measurements. With $\sim 10{,}000$ per run: $\sim 15$ experimental runs. Ground state tomography of 100-atom systems is feasible *right now*. Nobody knew this before these bounds were computed.

---

## Layer 3: The Deep Question (What Is Unsolved)

**The question:** *Why* are physical laws short?

This is the question that the theorem and the empirical observations point toward but cannot answer. It is one of the oldest and hardest questions in physics and philosophy. Here, precisely, is what we do and don't know.

**What we can prove (conditional):** IF physical laws have description length $K_F(\text{laws}) = L_\text{law}$, THEN physical states produced by those laws have $K_F(\text{state}) \leq L_\text{law} \cdot t + O(\text{overhead})$ where $t$ is evolution time, AND quantum state tomography costs $O(L_\text{law} \cdot t / \varepsilon)$ measurements. The "if" is the assumption. The "then" is our theorem.

**What we cannot prove:** Why $L_\text{law}$ is small. The Standard Model Lagrangian can be written on a napkin. Newton's second law is three symbols. Maxwell's equations are four. The laws of physics we have found are spectacularly short programs for spectacularly complex behavior. We did not derive this — we observed it.

**Three attempts at an answer:**

*The anthropic answer.* In a universe with long, complex laws ($K_F(\text{laws})$ large), no structure forms. No atoms, no stars, no life, no observers. Nobody asks the question. We find ourselves in a universe with short laws because only universes with short laws contain observers to notice. This is not an explanation — it is a selection filter. It tells you why we observe short laws without telling you why short laws exist.

*The mathematical universe answer.* Tegmark (2007) and Schmidhuber (1997) propose that all mathematically consistent universes exist, and we find ourselves in one that is both consistent and observable. Schmidhuber's "Speed Prior" explicitly weights universes by $2^{-K(\text{laws})}$ — shorter laws get more probability weight. In this view, the universe we observe is likely because it is compressible. Solomonoff's universal prior, applied to all of physics.

*The empirical terminus.* Maybe it just is. Some facts are axiomatic. The universe has local interactions — that's an input to physics, not an output. Asking "why local?" is like asking "why consistent?" There may be no deeper answer. 

**What is new in our work:** We do not answer why laws are short. We answer what follows *if* they are. And what follows is extremely concrete: the entire MDL framework, with computable bounds, exact numbers, and laboratory protocols. The philosophical question remains open. Its *consequences* for quantum information science are now fully derived.

---

## The Connection to Solomonoff (What Is Not New)

This needs to be said clearly because it is important for intellectual honesty.

Ray Solomonoff (1964) proved that the optimal prediction strategy for any sequence of observations is to weight hypotheses by $2^{-K(\text{hypothesis})}$ — the Solomonoff universal prior. This IS "science as MDL optimization." He proved it 60 years ago. The claim "science is finding minimum-description-length programs for data" is Solomonoff's theorem.

What Solomonoff could NOT do:
- $K$ (Kolmogorov complexity) is **uncomputable**. No algorithm can compute it. His result is an existence theorem.
- He handled only **classical** data. Quantum states are not classical bit strings.
- He gave **no sample complexity bounds**. How many observations until you find the right program? Unknown in his framework.

What our work adds:
- $K_F$ is **computable** with measured constants ($K_F \leq K + 577$ bits). The bound is not just theoretical — it is a specific number you can compute.
- We handle **quantum** data: density matrices, POVMs, Born-rule probabilities.
- We prove **tight sample complexity**: exactly $\Theta(K_F/\varepsilon)$ measurements. Not just existence, but a count.
- We give **exact numbers**: $K_F(|0\rangle) = 88$ bits, $K_F(\text{GHZ}_{10}) = 272$ bits, $K_F(\text{identity channel}) \approx 88$ bits regardless of $n$.

So: "Science is MDL" = Solomonoff 1964. "Quantum science uses a computable, physically motivated MDL with exact bounds" = our contribution.

---

## What "Physically Compressible" Actually Means

Here is the most concrete version of the claim.

Pick any physical system in nature. It could be a superconductor, a trapped ion chain, a Bose-Einstein condensate, the quantum state of an electron in a hydrogen atom. Whatever it is:

1. The process that made it — a local Hamiltonian, a sequence of laser pulses, a physical preparation — has a short description. $K_F(\text{process}) = O(\text{number of control parameters})$.

2. Because the process is short, the state is short: $K_F(\text{state}) \leq K_F(\text{process}) + \text{overhead}$. This is a theorem.

3. Because the state is short, you can learn it: $m^* = O(K_F(\text{state})/\varepsilon)$. This is also a theorem.

4. Because you can learn it, you can predict its behavior, engineer it, use it. This is what physics experiments do.

The entire enterprise of experimental physics — preparing states, measuring them, building models, making predictions — is feasible *because physical processes are compressible*. Every experiment that has ever worked is implicit evidence for low $K_F$.

If the universe were incompressible — if ground states of simple Hamiltonians required $10^{62}$ bits to specify — then measuring a quantum system would give you essentially no information about it. Every measurement would be noise. No experiment would tell you anything. Physics as a science would be impossible.

The fact that physics works — that experiments give reproducible results, that models generalize, that you can measure a system 1000 times and learn something about the 1001st measurement — is the empirical evidence that $K_F(\text{physical states})$ is small. Our theorem makes this precise: the compression ratio IS the measurement-reduction factor, exactly.

---

## The Born Rule Piece

There is one final component that is genuinely new and genuinely surprising.

The Born rule $P(\text{outcome} | \rho, M) = \text{Tr}(\rho \Pi_k)$ is not just "how quantum mechanics works." It is, as we prove (Theorem 3.1 of Saraff 2026f), the **unique** probability assignment rule for which quantum learning achieves the $K_F/\varepsilon$ bound. Any other Gleason-compatible rule either requires more measurements or makes some states unlearnable.

This means: the Born rule is not arbitrary. It is the *efficiency condition* on nature. It is the rule that says: **you may learn about any quantum state, and the cost of learning it is exactly proportional to the cost of describing it.** No more, no less.

Every quantum experiment ever performed — every photon counted, every spin measured, every quantum state tomographed — has implicitly validated this claim. The experiments work because the Born rule is efficient. You get exactly as much information from a measurement as the description length of the state allows. Nature is not hiding anything beyond what its compression ratio implies.

The Born rule has been derived before from symmetry (Gleason), from betting coherence (QBism), from information-theoretic axioms (Masanes et al.). Our derivation adds something different: the Born rule is the rule that makes quantum learning *efficient at the description-length rate*. Not just consistent. Not just unique. *Optimal*.

---

## Summary: Three Layers

| Layer | Claim | Status |
|---|---|---|
| **1** | $m^*(\rho, \varepsilon) = \Theta(K_F(\rho)/\varepsilon)$ | **Theorem. Proven. Tight.** |
| **2** | Physical states have $K_F \ll 4^n$ because physical processes are local | **Empirical fact. Measured. Not derived.** |
| **3** | Why physical laws are short | **Open question. 60 years old. Three candidate answers. No proof.** |

The slogan "physical reality is algorithmically compressible" is shorthand for all three layers at once. Taken literally as a proven theorem, it overstates. Taken as an empirical observation combined with the theorem's consequences, it is precisely correct. The universe is compressible, we can measure the compression ratio, and the theorem tells you exactly what that ratio buys you in measurements.

The compressibility is not slight. For 100 qubits, it is a factor of $10^{57}$. That is the difference between what physics experiments can do and what mathematics says is theoretically possible. The gap is $10^{57}$. The universe is nowhere near the theoretical maximum complexity. It is almost absurdly, improbably, structurally simple — and that simplicity is the reason science is possible.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*Layer 1 is proven in this paper series. Layer 2 is empirical with computable evidence. Layer 3 is a philosophical question with three candidate answers, none proven. All three are distinguished clearly throughout.*
