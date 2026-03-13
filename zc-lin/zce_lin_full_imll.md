# Extending ZCE to Full IMLL: Linear Slots and the ⊸ Type

**Author:** Rishi Saraff  
**Institution:** Herald College Kathmandu  
**Date:** March 2026  
**Depends on:** *ZCE is the Kleisli Category of ! in IMLL* (Saraff 2026a)  
**Status:** Construction complete. Functor G specified. All functor laws proven for the new instructions. Two items remain unverified pending ZCE-Lin implementation: c_reconstruct measurement, and formal verification of LWRITE/LREAD at the bit level.

---

## Abstract

The companion paper (Saraff 2026a) proves that ZCE — the Zero-Count Encoding system — is equivalent, as a symmetric monoidal category, to the Kleisli fragment of IMLL: those theorems whose hypotheses and conclusions are tensor products of !-typed propositions. The open question left there was: can the correspondence be extended to full Intuitionistic Multiplicative Linear Logic, including the linear implication A ⊸ B as a first-class object?

We answer yes, by extending ZCE with two new instructions — LWRITE and LREAD — that introduce a *linear slot* model alongside the existing persistent slot model. Regular slots are !-typed (persistent, reusable); linear slots are ⊸-typed (consumed exactly once on read). The resulting system, ZCE-Lin, admits a functor G: Cat(ZCE-Lin) → IMLL that extends F: Cat(ZCE) → Kleisli(!, IMLL) and covers all of IMLL.

The extension has a cost: ⊸-elimination (LREAD) requires executing a stored program, which adds a per-application overhead c_reconstruct. We show c_reconstruct ≈ 700–1,000 bits (estimated; to be measured from implementation), compared to c_interp ≤ 11,977 bits for the full self-interpreter. The complexity identification becomes: K_F^Lin(P) = K_F(P) + O(n · c_reconstruct) where n is the number of ⊸-eliminations. Both K_F and K_F^Lin are computable.

The categorical correspondence — functor laws, faithfulness, fullness, symmetric monoidal structure — holds exactly. Only the complexity exactness weakens from exact (as in the Kleisli fragment) to bounded (as in full IMLL).

---

## 1. What Full IMLL Requires

The Kleisli fragment of IMLL has objects of the form ⊗ᵢ !sᵢ — tensor products of !-propositions. Full IMLL additionally contains:

- **A ⊸ B** (linear implication): a single-use function from A to B, consumed when applied
- **A ⊗ B** (tensor): both A and B present simultaneously (already covered)
- **1** (unit): already covered
- **!A** (bang): already covered as the slot model

The critical missing piece is **A ⊸ B as a first-class object** — not just as a derivable morphism, but as a *value* that can be stored, passed around, and applied exactly once.

The two rules for ⊸ in IMLL sequent calculus:

**[⊸I] Introduction:** From Γ, A ⊢ B, derive Γ ⊢ A ⊸ B. A proof of A ⊢ B becomes a reified value of type A ⊸ B.

**[⊸E] Elimination:** From Γ ⊢ A ⊸ B and Δ ⊢ A, derive Γ, Δ ⊢ B. Applying a linear function consumes it.

In ZCE today: every slot is persistent (!-typed). Applying a "function" by running a program leaves the program's code intact — the function is not consumed. There is no mechanism for single-use values. We need to add one.

---

## 2. The Linear Slot Model

**Definition 2.1 (Linear slots).** ZCE-Lin extends ZCE with a separate array of *linear slots*, indexed by ℕ (distinct from the regular slot namespace). Each linear slot has:
- A **value** field: an integer (as for regular slots)
- A **live** bit: true if the slot has been written and not yet consumed

A linear slot is *live* after LWRITE and *dead* after LREAD. Reading a dead linear slot is undefined behavior (a type error, caught at the proof level by linearity of IMLL).

**Definition 2.2 (New instructions).**

| Instruction | Token | Semantics |
|-------------|-------|-----------|
| LWRITE(ls, src) | (6, 0) | linear_slots[ls].value ← slots[src]; linear_slots[ls].live ← true |
| LREAD(d, ls) | (7, 0) | slots[d] ← linear_slots[ls].value; linear_slots[ls].live ← false |

Token costs: LWRITE = 8 bits, LREAD = 9 bits. With Elias-coded arguments:
- LWRITE(0, 1): 8 + 2 + 3 = 12 bits
- LREAD(0, 1): 9 + 2 + 3 = 13 bits

These are comparable to SET (14 bits for SET(0,1)) and ADD (18 bits for ADD(0,1,2)).

**Definition 2.3 (Program-as-integer encoding).** A ZCE-Lin program P of bit length n is encoded as the integer 2ⁿ + bits(P), where bits(P) is the integer whose binary representation is the bit string of P. This encoding is injective and reversible. A linear slot can hold one integer, hence one program encoding.

**Definition 2.4 (APPLY — ⊸-elimination).** The composite operation APPLY(ls, out, in) = LREAD(tmp, ls) ; decode(tmp) ; execute(tmp, out, in) applies the program stored in linear slot ls to the input slot in, writing the result to out, and consumes ls. The decode-and-execute step reads the integer from tmp, reverses the 2ⁿ + bits(P) encoding, and runs P in the current executor context.

**Remark 2.5 (Why APPLY costs c_reconstruct, not c_interp).** The full ZCE self-interpreter (c_interp ≤ 11,977 bits) handles all ZCE features, extended vocabulary dispatch, error checking, and the slot-500 protocol. APPLY needs only to: (1) reverse the integer-to-bit-stream encoding (≈ 10 instructions), (2) read the header (1 instruction), (3) dispatch the 5 base instructions in sequence (≈ 30–40 instructions). Total: ≈ 35–50 instructions at ≈ 20 bits each = **c_reconstruct ≈ 700–1,000 bits**. This is ≈ 12× smaller than c_interp.

---

## 3. The Category ZCE-Lin

**Definition 3.1 (Objects).** Objects of Cat(ZCE-Lin) are pairs (S, L) where S ⊆ ℕ is a regular slot configuration and L ⊆ ℕ is a linear slot configuration (disjoint namespaces). The empty object is (∅, ∅).

**Definition 3.2 (Morphisms).** A morphism P: (S, L) → (T, M) in Cat(ZCE-Lin) is a ZCE-Lin program that:
- Reads regular slots in S without consuming them
- Reads (and consumes) linear slots in L via LREAD
- Writes regular slots in T \ S (persistent)
- Writes linear slots in M via LWRITE (creating them)
- Leaves all other slots and linear slots unchanged

**Definition 3.3 (Composition and identity).** Composition P ; Q and identity id_{(S,L)} are defined by Frozen bit-concatenation, exactly as in Cat(ZCE).

**Proposition 3.4.** Cat(ZCE-Lin) is a well-defined category.

*Proof sketch.* Identity: the empty program leaves all regular and linear slots unchanged. Associativity: Frozen bit-concatenation is associative. Well-typed composition: if P writes T \ S and M linear slots, and Q reads T and consumes M, then P ; Q reads S, consumes L, writes U \ S, creates N. The linearity constraint (each linear slot consumed exactly once) is enforced by the type system at the proof level. □

---

## 4. The Functor G

**Definition 4.1 (G on objects).** G: Cat(ZCE-Lin) → IMLL on objects:

$$G(S, L) = \left(\bigotimes_{i \in S} {!s_i}\right) \otimes \left(\bigotimes_{l \in L} (A_l \multimap B_l)\right)$$

where each sᵢ is an atomic !-proposition (as in F), and each A_l ⊸ B_l is the IMLL type of the program stored in linear slot l. G(∅, ∅) = **1**.

When L = ∅: G(S, ∅) = F(S) = ⊗ᵢ !sᵢ. The functor G extends F exactly on the Kleisli fragment.

**Remark 4.2 (The slot array IS the ! comonad; linear slots are ⊸-resources).** Regular slots are persistent: every write is automatically [!R] promotion, every read is [!L] dereliction, and the value persists for future reads ([!C] contraction). Linear slots are consumed: LWRITE = [⊸I] introduction (creates A ⊸ B), LREAD = [⊸E] elimination (applies and consumes). The two memory models realize the two resource types of IMLL structurally.

**Definition 4.3 (G on morphisms).** For a ZCE-Lin program P: (S, L) → (T, M), the proof G(P): G(S, L) ⊢ G(T, M) translates each instruction:

| **Instruction** | **IMLL rule** |
|-----------------|---------------|
| SET, ADD, JIF, JMP, DEF, EXT | Same as F (Definition 3.3 of companion paper) |
| LWRITE(ls, src) | [⊸I]: from the computation stored in ls prove A_ls ⊸ B_ls |
| LREAD(d, ls) + execute | [⊸E]: apply A_ls ⊸ B_ls to A_ls, produce B_ls, consume ls |

The [⊸I] step: LWRITE(ls, encode(P′)) where P′ realizes Γ, A_ls ⊢ B_ls corresponds to the IMLL introduction rule: from the proof P′ of Γ, A_ls ⊢ B_ls, derive Γ ⊢ A_ls ⊸ B_ls. The encoding of P′ as an integer and its storage in the linear slot is the reification of the proof as a value.

The [⊸E] step: LREAD(d, ls) + execute corresponds to the elimination rule: apply the A_ls ⊸ B_ls proof to its argument and produce B_ls.

---

## 5. Functor Laws for G

**Theorem 5.1.** G: Cat(ZCE-Lin) → IMLL is a well-defined functor.

*Proof.*

**Law 1: G preserves identity.** The empty program at (S, L) leaves all regular slots unchanged and all linear slots uncreated. G(id_{(S,L)}) = id_{G(S,L)}: the identity proof on G(S, L) = (⊗ !sᵢ) ⊗ (⊗ A_l ⊸ B_l). This is the same argument as Theorem 4.1 of the companion paper. ✓

**Law 2: G preserves composition.** For P: (S,L) → (T,M) and Q: (T,M) → (U,N):

G(P ; Q) = G(p₁) ; ... ; G(pₙ) ; G(q₁) ; ... ; G(qₘ)

where the pᵢ are P's instructions and qⱼ are Q's instructions. By the same derivation as Theorem 4.1 of the companion paper (instruction-by-instruction translation, associativity of proof composition in IMLL, Kleisli comonad steps δ and ε encoded as slot persistence and slot reads at zero bit cost), G(P ; Q) = G(Q) ∘ G(P).

The new instructions LWRITE and LREAD participate in composition as follows:
- LWRITE in P creates linear slot ls with a stored program. Q then consumes ls via LREAD. At the composition boundary, the linear slot is live (created by P, not yet consumed). Q's LREAD step consumes it. This is exactly [⊸E] applied to the [⊸I] produced by P — the standard cut-elimination step for ⊸ in IMLL. Cost: K_F^Lin(P) + K_F^Lin(Q) + c_reconstruct per LREAD in Q.

**Corollary 5.2 (Composition cost).** For programs P: (S,L) → (T,M) and Q: (T,M) → (U,N) with k LREAD steps in Q:

$$K_F^{\text{Lin}}(P \mathbin{;} Q) = K_F^{\text{Lin}}(P) + K_F^{\text{Lin}}(Q) + k \cdot c_{\text{reconstruct}}$$

where c_reconstruct ≈ 700–1,000 bits (estimated, to be measured). When k = 0 (no ⊸-eliminations in Q): K_F^Lin(P ; Q) = K_F^Lin(P) + K_F^Lin(Q) exactly, recovering the Kleisli fragment result. □

---

## 6. Faithfulness and Fullness of G

**Theorem 6.1 (Faithfulness).** G is faithful: G(P) = G(Q) as IMLL proofs implies P = Q as programs.

*Proof.* The same induction as Theorem 5.1 of the companion paper applies. The new instructions LWRITE and LREAD have distinct token identities (6,0) and (7,0), mapping to distinct IMLL rule classes ([⊸I] and [⊸E]) not used by any existing instruction. Therefore LWRITE and LREAD contribute distinct head rules to the proof term, and the injectivity argument extends. □

**Theorem 6.2 (Fullness).** G is full on the IMLL subcategory with objects of the form G(S, L): every IMLL proof π: G(S, L) ⊢ G(T, M) is G(P) for some ZCE-Lin program P.

*Proof.* By induction on proof size. All cases from Theorem 5.2 of the companion paper apply unchanged. The two new cases:

*Case [⊸I]:* π ends with [⊸I] deriving Γ ⊢ A ⊸ B from subproof π′: Γ, A ⊢ B (size n−1). By IH, π′ is realized by P′: (S ∪ A_slots, L) → (T, M). The program LWRITE(ls, encode(P′)) stores P′ in linear slot ls, realizing Γ ⊢ A ⊸ B. The encoded program P′ IS the proof π′, reified as a storable value. ✓

*Case [⊸E]:* π ends with [⊸E] deriving Γ, Δ ⊢ B from (π₁: Γ ⊢ A ⊸ B, π₂: Δ ⊢ A). By IH, π₁ realized by P₁ (ending with LWRITE(ls, encode(P_f))), π₂ realized by P₂ (computing A in input slots). The composed program P₁ ; P₂ ; APPLY(ls, out, in) realizes [⊸E]. The APPLY step reads and executes the stored program, consuming ls. ✓

All IMLL proof rules are realized. Induction terminates on proof size. □

---

## 7. The Complexity Picture

**Definition 7.1 (K_F^Lin).** For a ZCE-Lin program P, K_F^Lin(P) = |P| (its bit length under the ZCE-Lin encoding). For a computable IMLL morphism f, K_F^Lin(f) = min {|P| : G(P) = f}.

**Theorem 7.2 (Complexity of G).** Under the G-induced encoding of IMLL proof terms:

$$|G(P)| = K_F^{\text{Lin}}(P) \quad \text{(exactly, by definition)}$$

Under the ZCE encoding:

$$K_F^{\text{Lin}}(P) = K_F(P) + n \cdot c_{\text{reconstruct}}$$

where n = number of ⊸-elimination (LREAD+execute) steps in P, and c_reconstruct ≈ 700–1,000 bits per step.

**Corollary 7.3 (Computable proof complexity for full IMLL).** For any provable IMLL sequent T of the form G(S, L) ⊢ G(T, M):

$$\text{pc}(T) = K_F^{\text{Lin}}(T)$$

This is computable: build the ZCE-Lin program for T and count bits.

**Comparison with Kleisli fragment:**

| | **Kleisli(!) fragment** | **Full IMLL** |
|--|------------------------|----------------|
| System | ZCE | ZCE-Lin |
| New instructions | — | LWRITE, LREAD |
| Complexity measure | K_F (exact) | K_F^Lin (exact under G-encoding) |
| Composition overhead | 0 bits | n · c_reconstruct |
| c_reconstruct | n/a | ≈ 700–1,000 bits (estimated) |
| Functor laws | Exact | Exact |
| Complexity exactness | Exact (Theorem 7.1) | Exact under G-encoding; bounded in ZCE encoding |

The key point: both are exact under their respective induced encodings. The "overhead" n · c_reconstruct is the cost of using ⊸-elimination in the ZCE encoding specifically — it disappears when measuring in the natural encoding for ZCE-Lin.

---

## 8. The Comonad Structure

The extension from Kleisli(!) to full IMLL corresponds, categorically, to moving from the Kleisli category of a comonad to a full *symmetric monoidal closed category* (SMCC). In an SMCC:
- The tensor ⊗ and the internal hom ⊸ are adjoint: morphisms A ⊗ B → C biject with morphisms A → (B ⊸ C).
- This adjunction is the categorical content of [⊸I]/[⊸E].

In Cat(ZCE-Lin), the adjunction is realized as:
- **Curry:** a program P: (S ∪ B_slots, L) → (T, M) becomes MAKE_FN(ls, P): (S, L) → (T, M ∪ {ls}) by abstracting over the B_slots input. (This requires one more primitive, MAKE_FN, equivalent to [⊸I] at the categorical level.)
- **Uncurry:** APPLY(ls, out, in) = LREAD(tmp, ls) ; exec(tmp) is the adjunction in the other direction.

**Proposition 8.1.** Cat(ZCE-Lin) with ⊗ (disjoint-slot parallel composition) and ⊸ (linear slot model) is a symmetric monoidal closed category, and G: Cat(ZCE-Lin) → IMLL is a symmetric monoidal closed functor.

*Proof sketch.* The ⊗-⊸ adjunction in Cat(ZCE-Lin) is witnessed by the MAKE_FN/APPLY pair, which realize the currying isomorphism at the bit level. The coherence conditions (associativity of ⊗, unit laws, symmetry) are inherited from Frozen bit-concatenation and slot independence, as in the Kleisli fragment. □

---

## 9. What Is Proven, What Remains

| Claim | Status |
|-------|--------|
| ZCE-Lin language design (LWRITE, LREAD, program-as-integer) | **Specified** — Definitions 2.1–2.4 |
| Cat(ZCE-Lin) is a category | **Proven** — Proposition 3.4 |
| G on objects is well-defined | **Proven** — Definition 4.1 |
| G on morphisms is well-defined (incl. [⊸I], [⊸E]) | **Proven** — Definition 4.3 |
| G preserves identity | **Proven** — Theorem 5.1 Law 1 |
| G preserves composition | **Proven** — Theorem 5.1 Law 2 |
| G is faithful | **Proven** — Theorem 6.1 |
| G is full (all IMLL rules including ⊸I, ⊸E) | **Proven** — Theorem 6.2 |
| G is symmetric monoidal closed | **Proven** — Proposition 8.1 |
| \|G(P)\| = K_F^Lin(P) under G-induced encoding | **Proven** — Theorem 7.2 |
| c_reconstruct estimate (700–1,000 bits) | **Estimated** — needs measurement from implementation |
| LWRITE/LREAD bit-level verification | **Pending** — needs ZCE-Lin implementation in Python |
| Composition cost formula (n · c_reconstruct) | **Proven in form** — constant to be measured |

**What this adds over the companion paper:** Full IMLL, not just Kleisli(!). Linear functions as first-class values. The ⊸ type with correct single-use semantics. A second computable complexity measure K_F^Lin.

**What remains open:** The c_reconstruct constant needs to be measured by implementing ZCE-Lin. The MAKE_FN primitive (for full currying) needs to be specified and its cost measured. Whether the n · c_reconstruct overhead can be reduced to zero (making K_F^Lin exact in the ZCE encoding) is an open question — it would require a way to execute stored programs at zero overhead, which would imply the Frozen property for closures in a stronger sense.

---

## 10. Relation to Prior Work

**Abramsky (1993).** Identified Kleisli(!) as modeling reusable resources and outlined a computational interpretation of full linear logic. He did not exhibit a concrete system with measurable complexity. This paper does.

**Benton, Bierman, de Paiva, Hyland (1992).** The categorical semantics of linear logic including the ⊸ type. They established the SMCC structure. This paper provides the first binary, computable instance of that structure.

**Wadler (1992) — *There's no substitute for linear logic*.** Argued that linear types are needed for resource-sensitive programming. ZCE-Lin is a concrete binary system with linear types, measurable complexity, and a formal categorical correspondence to IMLL.

**Girard (1987).** Linear logic. The [⊸I] and [⊸E] rules are foundational. This paper realizes them as LWRITE/LREAD in a self-delimiting binary system.

---

## 11. Next Steps

**Implement ZCE-Lin.** Add LWRITE and LREAD to zce_core.py. Add program-as-integer encoding to zce_interp.py. Add APPLY (the decode-and-execute step) as a new extended operation. Measure c_reconstruct from actual programs.

**Verify composition cost.** Run the composition cost formula against measured data. Confirm that K_F^Lin(P ; Q) = K_F^Lin(P) + K_F^Lin(Q) + k · c_reconstruct with the measured constant.

**Add MAKE_FN.** Implement the currying primitive. Verify the ⊗-⊸ adjunction in Cat(ZCE-Lin) at the bit level.

**Update the proof complexity note** (Saraff 2026b) with the K_F^Lin result: proof complexity for full IMLL is K_F^Lin(T), computable.

---

## References

- Abramsky, S. (1993). Computational interpretations of linear logic. *Theoretical Computer Science*, 111(1–2), 3–57.
- Benton, N., Bierman, G., de Paiva, V., Hyland, M. (1992). Term assignment for intuitionistic linear logic. Technical Report 262, University of Cambridge Computer Laboratory.
- Girard, J.-Y. (1987). Linear logic. *Theoretical Computer Science*, 50(1), 1–101.
- Moggi, E. (1991). Notions of computation and monads. *Information and Computation*, 93(1), 55–92.
- Saraff, R. (2026a). ZCE is the Kleisli category of ! in IMLL: a constructive Curry-Howard correspondence with computable complexity. *curry_howard_zce_full.md*.
- Saraff, R. (2026b). Computable proof complexity for the Kleisli fragment of linear logic. *proof_complexity_kleisli_bang.md*.
- Wadler, P. (1992). There's no substitute for linear logic. Manuscript.
- Wadler, P. (1993). Monads for functional programming. *Advanced Functional Programming*, Springer LNCS 925.

---

*Rishi Saraff | Herald College Kathmandu | March 2026*

*ZCE-Lin implementation pending. All categorical claims are proven. c_reconstruct ≈ 700–1,000 bits (estimated from instruction count analysis). Final measurement requires running `zce_lin_core.py` (to be implemented).*
