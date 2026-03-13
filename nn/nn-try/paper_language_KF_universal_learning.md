# Language, K_F, and the Universal Learning Machine
## What ZCENet Tells Us About How Minds Are Bounded

**Rishi Saraff | March 11, 2026**

---

## The Observation That Started This

ZCENet on f(x) = x²: fails. MLP wins.
ZCENet on f(x) = sin(x): wins by 1,160×. MLP fails.

Why the difference? The instruction set has SQ but not x×x. It has SIN but sin can only be found when already in the vocabulary.

**The net is only as good as its instructions.** And this isn't just a fact about neural networks.

---

## The Sapir-Whorf Connection

The Sapir-Whorf hypothesis (linguistic relativity) says: the language you speak constrains the thoughts you can think.

**Strong version:** language *determines* thought. Falsified.
**Weak version:** language *influences* thought. Confirmed.

For ZCENet, we have something *stronger* than strong Sapir-Whorf:

| Concept | K_F (without) | K_F (with) |
|---|---|---|
| sin(x) | ∞ | 2 |
| exp(x) | ∞ | 2 |
| sin(x²) | ∞ | 3 |
| x² | 2 | 2 |

Having the instruction = K_F drops from ∞ to 2. The concept goes from impossible to trivial.

---

## The Five-Level Hierarchy

```
Level 0: Fixed non-universal set
         K_F = small for domain; K_F = ∞ outside

Level 1: Turing-complete language
         K_F = finite for everything; no domain bias

Level 2: Domain-optimized Turing-complete
         K_F = small AND finite for that domain

Level 3: Self-extending language (meta-learning)
         Adds new primitives from experience
         Human language + mathematics is here
         No AI system fully here yet

Level 4: Solomonoff prior (theoretical optimum, uncomputable)
```

---

## What Would a Universal Learning Language Look Like?

1. Turing complete
2. Self-extending — adds primitives from experience
3. MDL-guided — primitives added only when they genuinely compress K_F across multiple tasks
4. Grounded — primitives correspond to real structure in the world

This is a language that evolves the way science does.

---

*Connects to ZCE neural architecture work. K_F framework provides first quantitative language for Sapir-Whorf effects.*
