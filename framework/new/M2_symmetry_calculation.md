# M=2 Symmetry Calculation — Working Document

**Purpose:** Determine the symmetry group of the M=2 level from token
structure alone. Specifically: is M=2 self-similar to M=1 (SU(2))?

---

## Step 1: What does the token structure say about M=2?

A token at depth M=2 is [0^N 11 0].

The M-run at M=2 is: **11** — two identical 1-bits.

Compare:
- M=1: M-run is **1** — one 1-bit
- M=2: M-run is **11** — two 1-bits
- M=3: M-run is **111** — three 1-bits

The 1-bits within a single token's M-run are structurally identical.
There is no way to distinguish the first 1-bit from the second 1-bit
within [0^N 11 0] — the Frozen decoder just counts them.
They carry no individual identity. They are indistinguishable.

This is the key structural fact we will use.

---

## Step 2: What space do M=1 states span?

From the P6 argument in proofs.md:

The minimum set at M=1 giving new symmetry is {(0,1), (1,1)}.
These two states span a 2-dimensional complex space ℂ².
Call this space V₁ = ℂ².
The symmetry group acting on V₁ is SU(2).

Basis of V₁:
- |e₁⟩ = |(0,1)⟩   [N=0, one 1-bit]
- |e₂⟩ = |(1,1)⟩   [N=1, one 1-bit]

---

## Step 3: What space do M=2 states span — naively?

The states at M=2 are: (0,2), (1,2), (2,2), (3,2), ...
Each has two 1-bits in the M-run.

If we take the minimum set at M=2 giving new symmetry,
we might naively take {(0,2), (1,2), (2,2)} — three states,
spanning a 3-dimensional space ℂ³, with symmetry SU(3).

But wait. This is exactly what we are trying to test.
The question is: are these three states genuinely independent,
or are they constructively built from M=1 states?

---

## Step 4: The Construction Argument

Here is the key observation from the token structure.

A token at M=2 has two 1-bits. The Frozen decoder reads:
- First: N zeros (identity)
- Then: two 1-bits (depth run)
- Then: terminating zero

The two 1-bits are added one at a time in the sequential
reading. The token [0^N 11 0] is, from the decoder's perspective,
the result of reading [0^N 1 ...] and then reading one more 1-bit.

In other words: an M=2 token is an M=1 token with one additional
1-bit appended before the terminating zero.

**Formal statement:**
Token(N, M=2) = Token(N, M=1) with one 1-bit inserted before
the final 0.

This means M=2 states are not independently constructed —
they are M=1 states extended by one step.

---

## Step 5: The Symmetric Square

Here is where the group theory enters.

If M=2 states are "M=1 states with one more 1-bit," then the
natural space for M=2 states is not a new independent ℂ³,
but rather the space of **symmetric combinations of two M=1 states**.

Why symmetric? Because the two 1-bits in the M-run are
indistinguishable (Step 1). Swapping them does nothing — there
is no physical difference between "first 1-bit then second 1-bit"
and "second 1-bit then first 1-bit" when both are identical.

The space of symmetric combinations of two copies of V₁ = ℂ²
is called the **symmetric square** of ℂ²:

    Sym²(ℂ²) = the symmetric tensor product of ℂ² with itself

**Computing Sym²(ℂ²):**

The full tensor product ℂ² ⊗ ℂ² has dimension 2×2 = 4.
It decomposes into:
- Symmetric part: Sym²(ℂ²) — dimension 3
- Antisymmetric part: Alt²(ℂ²) — dimension 1

So Sym²(ℂ²) is 3-dimensional.

Basis of Sym²(ℂ²):
- |e₁⟩⊗|e₁⟩                        [both bits in state e₁]
- (1/√2)(|e₁⟩⊗|e₂⟩ + |e₂⟩⊗|e₁⟩)   [symmetric combination]
- |e₂⟩⊗|e₂⟩                        [both bits in state e₂]

These are 3 basis states. So Sym²(ℂ²) has dimension 3.

---

## Step 6: What is the symmetry group of Sym²(ℂ²)?

SU(2) acts on V₁ = ℂ² by its fundamental representation.
This action induces an action on Sym²(ℂ²) — the spin-1
representation of SU(2).

**Key fact from representation theory:**
The symmetric square of the fundamental representation of SU(2)
is the spin-1 (adjoint) representation of SU(2).

Concretely: if g ∈ SU(2) acts on ℂ² as a 2×2 matrix,
it acts on Sym²(ℂ²) as a 3×3 matrix — the spin-1 representation.

The symmetry group of Sym²(ℂ²) *as an SU(2) module* is still SU(2).

**This is the critical result:**
The symmetry group of M=2 is SU(2) — the same as M=1.
M=2 is self-similar to M=1. □ (conditional — see below)

---

## Step 7: Checking the dimension — does it match?

At M=2 we get Sym²(ℂ²) which is 3-dimensional.
At M=1 we had ℂ² which is 2-dimensional.

So M=2 has MORE states (dimension 3 vs 2) but the SAME
symmetry group (SU(2) in both cases).

This makes sense: Sym²(ℂ²) is a representation of SU(2),
just a higher-dimensional one. It does not introduce a new
group.

---

## Step 8: What about M=3?

Following the same logic:

M=3 tokens have three identical 1-bits in the M-run.
M=3 states are "M=2 states with one more 1-bit."

The natural space for M=3 states is:
Sym³(ℂ²) — the symmetric cube of ℂ².

**Computing Sym³(ℂ²):**

Sym³(ℂ²) has dimension C(2+3-1, 3) = C(4,3) = 4.

Basis:
- |e₁e₁e₁⟩
- (1/√3)(|e₁e₁e₂⟩ + |e₁e₂e₁⟩ + |e₂e₁e₁⟩)
- (1/√3)(|e₁e₂e₂⟩ + |e₂e₁e₂⟩ + |e₂e₂e₁⟩)
- |e₂e₂e₂⟩

Dimension = 4. This is the spin-3/2 representation of SU(2).

The symmetry group of Sym³(ℂ²) as an SU(2) module is still SU(2).

**PROBLEM:** This gives SU(2) again at M=3, not SU(3).

---

## Step 9: The Problem with the Symmetric Power Approach

If we continue this logic:
- M=1: ℂ² — spin-1/2 rep of SU(2), dim=2
- M=2: Sym²(ℂ²) — spin-1 rep of SU(2), dim=3
- M=3: Sym³(ℂ²) — spin-3/2 rep of SU(2), dim=4
- M=k: Symᵏ(ℂ²) — spin-k/2 rep of SU(2), dim=k+1

All of these have symmetry group SU(2).
We never get SU(3) from this construction.

**This is a genuine problem with Path B.**

The symmetric power construction gives us SU(2) at every M level.
It explains why M=2 is self-similar to M=1 (good) but it cannot
explain why M=3 gives SU(3) (bad).

---

## Step 10: What went wrong? Diagnosing the failure.

The symmetric power approach assumed:
*M=k states are symmetric combinations of k copies of M=1 states.*

This assumption may be wrong. Let us examine it.

**Why it might be wrong:**

The M-run at M=k is k identical 1-bits. We treated this as
"k copies of one 1-bit" — k copies of the M=1 structure.

But an M=k token is not k separate M=1 tokens concatenated.
It is a SINGLE token with a run of k ones.

The run [111...1] (k ones) is a single unbroken structure.
It is not k separate objects that happen to be next to each other.

**The alternative reading:**

The M-run [1^k 0] is itself a self-contained binary structure.
It has its own internal symmetry — the symmetry of the space
of all binary strings of length k ending in 0.

But this does not obviously give us U(1), SU(2), SU(3) either.

---

## Step 11: Back to Decision Point — Two Alternative Paths

**Path A (revised):** Constructive dependence via composition

Instead of symmetric powers, think about how tokens at different
depths are COMPOSED in the lattice.

A transition from (N, M) to (N, M+1) adds one 1-bit to the M-run.
This is a single elementary step in the lattice.

The structure of these elementary steps, and what algebra they generate,
might give us the right groups.

Specifically: the algebra generated by single-step M-transitions
starting from M=0 might naturally produce:
- At depth 1: the algebra of one generator → U(1) or SU(2)?
- At depth 2: the algebra of two generators → ?
- At depth 3: the algebra of three generators → SU(3)?

This requires thinking about what algebra the M-direction
transitions generate.

**Path C (honest fallback):**

Accept that the symmetric power argument correctly handles M=2
(self-similar to M=1) but cannot handle M=3. Acknowledge that
M=3 → SU(3) requires an additional argument not yet found.

Document exactly what IS proven:
- M=2 is self-similar to M=1 (the Sym²(ℂ²) argument — but see
  the problem in Step 9)
- Actually even M=2 self-similarity via this route says Sym²(ℂ²)
  has SU(2) symmetry as an SU(2) module — but is SU(2) the FULL
  symmetry group of Sym²(ℂ²) as an abstract space?

---

## Step 12: Correcting the Symmetry Group Calculation

This is the question we should have asked earlier.

**What is the FULL symmetry group of Sym²(ℂ²) as an abstract
vector space, independent of how SU(2) acts on it?**

Sym²(ℂ²) is a 3-dimensional complex vector space.
The full symmetry group of a 3-dimensional complex vector space is U(3),
with special unitary part SU(3).

So:
- As an abstract 3-dimensional space: symmetry = SU(3)
- As an SU(2) module: the SU(2) action is a subgroup of SU(3)

**This changes everything.**

The question is: which symmetry group is the NATURAL one for M=2?

- If we ask "what is the symmetry of M=2 states as an abstract space?" → SU(3)
- If we ask "what is the inherited symmetry from M=1?" → SU(2) subgroup

**Decision Point:** Which question is the right one to ask?

---

## Step 13: The Right Question

The token framework cares about INTRINSIC structure.

The M=2 states get their intrinsic structure from the token encoding.
Their token structure does NOT come with an SU(2) action attached —
the SU(2) action was something WE defined by saying "take pairs at M=1."

The M=2 states, by themselves, are a set of states with two identical
1-bits. Their intrinsic symmetry is the symmetry of their own space
as an abstract complex vector space — which is SU(3) for a 3-dimensional
space (from the minimum set argument).

But wait — the minimum set at M=2 from the token structure alone
is not obviously 3. We need to rederive it.

**Minimum set at M=2:**

By the same argument as M=1:
- One M=2 state has the same U(1) symmetry as one M=0 or M=1 state.
  Not new.
- Two M=2 states span ℂ². Symmetry SU(2). Same as M=1. Not new.
- Three M=2 states span ℂ³. Symmetry SU(3). NEW — not isomorphic
  to U(1) or SU(2).

So the minimum set at M=2 giving genuinely new symmetry is 3 states,
giving SU(3).

**But then M=2 gives SU(3), not M=3.**

---

## Step 14: The Real Conclusion So Far

Following the minimum-new-symmetry argument:
- M=0: minimum 1 state → U(1)
- M=1: minimum 2 states → SU(2)  [new: SU(2) ≇ U(1)]
- M=2: minimum 3 states → SU(3)  [new: SU(3) ≇ SU(2)]
- M=3: minimum 4 states → SU(4)  [new: SU(4) ≇ SU(3)]

This gives SU(k+1) at depth M=k. That is NOT the SM structure.
The SM has SU(3) at M=3, not M=2.

**We have a real problem.**

The minimum-new-symmetry argument gives the WRONG answer for
the SM. It places SU(3) at M=2, but the SM has SU(3) at M=3.

---

## Step 15: Honest Assessment

**What the symmetric power approach showed (Step 5-9):**
If M=k states are symmetric combinations of k M=1 states,
all M-levels give SU(2). Never SU(3). Wrong.

**What the minimum-new-symmetry approach showed (Step 13-14):**
The minimum set giving new symmetry at M=k has k+1 states.
This gives U(1), SU(2), SU(3), SU(4), ... at M=0,1,2,3,...
This puts SU(3) at M=2, not M=3. Wrong for the SM.

**Neither approach gives U(1) at M=0, SU(2) at M=1, SU(3) at M=3.**

---

## Step 16: What Might Actually Work

The problem with both approaches is that they do not use something
specific about the token [0^N 1^M 0]: the relationship between
N and M in the SAME token.

The token has both N zeros and M ones. They are not independent
— they appear together in the same token. A state at (N, M) has
BOTH an identity (N) and a depth (M).

Perhaps the right question is not "what is the symmetry of the
M-row" but "what is the symmetry of the joint (N,M) structure
at each depth, where both N and M vary?"

**A new approach: joint (N,M) symmetry**

Consider the set of all tokens at a given token LENGTH L = N+M+1.

At L=1: only (0,0). One token.
At L=2: (0,1) and (1,0). Two tokens.
At L=3: (0,2), (1,1), (2,0). Three tokens.
At L=4: (0,3), (1,2), (2,1), (3,0). Four tokens.

The number of tokens at length L is exactly L (for L≥1).

The symmetry group of L states (the L tokens at length L) is SU(L).

So:
- Length 1: 1 token → U(1)
- Length 2: 2 tokens → SU(2)
- Length 3: 3 tokens → SU(3)
- Length 4: 4 tokens → SU(4)

And by the self-similarity argument:
SU(4) ⊃ SU(3)×U(1), so length 4 gives no new independent structure.

**This gives U(1), SU(2), SU(3) at lengths 1, 2, 3 and self-similarity
from length 4 onward.**

But: this assigns groups by token LENGTH, not by depth M.
The SM groups are assigned to depth levels M=0, 1, 3, not to lengths.

**However:** the minimum non-trivial tokens at each group level are:
- U(1): length-1 token → (0,0) which has M=0
- SU(2): length-2 tokens → (0,1) and (1,0); the M=1 token is (0,1)
- SU(3): length-3 tokens → (0,2), (1,1), (2,0); includes M=2 and M=1

This still doesn't isolate M=3.

---

## Conclusion: Honest Dead End for Now

**What we have established:**
1. The symmetric power approach: M=2 has SU(2) symmetry *as an
   SU(2) module* but SU(3) as an abstract space. Ambiguous.
2. The minimum-new-symmetry approach: gives SU(k+1) at M=k.
   Places SU(3) at M=2, not M=3. Disagrees with SM.
3. The token-length approach: gives U(1), SU(2), SU(3) at
   lengths 1, 2, 3 — correct groups but not cleanly at M=0,1,3.

**What we have NOT found:**
A derivation from the token structure alone that gives SU(3)
specifically at depth M=3 (and not at M=2).

**The honest conclusion:**
The claim that M=3 gives SU(3) (rather than M=2) may require
either:
(a) Additional physical input (which would make it not a pure
    derivation), or
(b) A more careful definition of what "depth level" means
    physically — perhaps depth M is not counted by the M-run
    length but by something else in the token structure.

**This is a genuine open problem. It will be recorded as such
in proofs.md.**

---

*Working document — all dead ends recorded.*
*Date: March 2026*
