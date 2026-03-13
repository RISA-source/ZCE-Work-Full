# P6 Decision Map
## Why M=1 gives pairs and M=3 gives triplets — tracing every decision point

**Purpose:** Before writing the proof, map every place where a choice is made,
what each choice forces, and why we take the path we take.
No skipped steps. No assumed conclusions.

---

## The Question

We have the (N,M) lattice. At each row M, we have states:
(0,M), (1,M), (2,M), (3,M), ...

We want to prove that these rows naturally group into:
- M=0 → singletons (dimension 1) → symmetry group U(1)
- M=1 → pairs (dimension 2) → symmetry group SU(2)
- M=3 → triplets (dimension 3) → symmetry group SU(3)

Using ONLY what the token structure forces. No SM knowledge allowed as input.

---

## Starting Point: What the Token Actually Is

A token [0^N 1^M 0] has three parts:
- N leading zeros — the identity run
- M ones — the depth run
- one terminating zero — the boundary

The bit-length is N + M + 1.

**Key structural fact:** Within a fixed M-row, the only thing that differs
between tokens (0,M), (1,M), (2,M), ... is the N-count. The M-run is
identical for all of them — it is always M ones.

**Key structural fact:** Within a fixed N-column, the only thing that
differs between tokens (N,0), (N,1), (N,2), ... is the M-count.

This means:
- N labels *which entity* (horizontal direction)
- M labels *how deep* the entity is (vertical direction)

---

## Decision Point 1: What does "grouping" mean?

**The question:** When we say M=1 states "group into pairs," what does
that mean formally? We need a definition that comes from the token
structure, not from our knowledge of SU(2).

**Option A:** Grouping by token length.
States at (N,M) have token length N+M+1. At M=1: lengths are
2, 3, 4, 5, ... (for N=0,1,2,3,...). All different lengths.
No natural grouping into same-length sets at a given M.
→ This doesn't give pairs. **Eliminated.**

**Option B:** Grouping by the minimum distinguishing operation.
What is the minimum operation on the token structure that moves
between states at the same M-level?
At M=1: going from (N,1) to (N+1,1) costs exactly one zero bit —
add one zero to the N-run.
This defines adjacency: (N,M) and (N+1,M) are adjacent.
→ This gives a line graph structure, not pairs. **Not what we want.**

**Option C:** Grouping by what is needed to instantiate M at all.
To have M=1 exist as a physically meaningful level —
distinguishable from M=0 — you need a minimum number of
states that together witness the M=1 structure.
**This is the promising direction.** Pursue below.

**Option D:** Grouping by the symmetry of the M-run itself.
The M-run is M identical 1-bits. The symmetry of M identical
objects is the symmetric group S_M. But we want unitary groups,
not symmetric groups.
→ This gives the wrong group type. **Eliminated as stated,
but the idea of counting M-bits is worth keeping.**

**Decision:** Pursue Option C — grouping by what is needed to
instantiate the M-level. But we must make this precise.

---

## Decision Point 2: What does it mean to "instantiate" a depth level?

**The question:** What is the minimum set of states that makes depth
level M physically meaningful — i.e., that gives M an independent
existence, not reducible to M-1?

**Attempt at definition:**
Depth level M is instantiated by a set S of states if:
1. Every state in S has depth exactly M.
2. The states in S are mutually distinguishable (Named).
3. The M-level structure of S cannot be reduced to M-1 level structure.

Condition 3 is the hard one. We need to make it precise.

**What does "cannot be reduced to M-1" mean?**

**Option C1:** M is irreducible to M-1 if there is no injective map
from S to any set of M-1 states that preserves the token structure.

This is too strong — there is always an injective map between
countable sets. **Eliminated.**

**Option C2:** M is irreducible to M-1 if the symmetry group of S
is not isomorphic to the symmetry group of any M-1 level set.

This is circular — it presupposes we know the symmetry groups,
which is what we are trying to derive. **Eliminated.**

**Option C3:** M is irreducible to M-1 if the *minimum number of
states* needed to witness M-level structure is strictly greater
than the minimum needed to witness (M-1)-level structure.

This is promising. It grounds dimension in a counting argument.
**Pursue this.**

---

## Decision Point 3: What is the "minimum number of states" at each level?

**The question:** For each M, what is the smallest set of states that
is not reducible to M-1?

**At M=0:**
The M=0 level has zero 1-bits. The token is [0^N 0] = [0^(N+1)].
Wait — this is just N+1 zeros with no 1-bits. The minimum state
at M=0 is (N=0, M=0) = [0] = one bit.
To have a meaningful M=0 level (not just the empty token), we
need at least one state. Minimum = **1 state**.
One state spans a 1-dimensional space.

**At M=1:**
The M=1 level has exactly one 1-bit. The minimum token structure
at M=1 is the single token (N=0, M=1) = [10].

But: is one state at M=1 sufficient to make M=1 irreducible to M=0?

One state at M=1 means: one object with one 1-bit. This object
has a definite identity (N=0) and a definite depth (M=1). But
its depth M=1 only has meaning relative to M=0 — "one 1-bit"
only makes sense as distinct from "zero 1-bits."

**Decision Point 3a: Does one state at M=1 instantiate M=1?**

If we have only (N=0, M=1), can we distinguish "being at M=1"
from "being at M=0"? Yes — the token is [10] vs [0], they are
different bit strings. Named is satisfied.

But the question is about the *symmetry structure* of M=1, not
just its existence. A single state has only a U(1) symmetry
(phase rotation). That is the same as M=0.

→ One state at M=1 gives no new symmetry. It is self-similar to M=0.

**So: how many states are needed at M=1 to give a symmetry not
present at M=0?**

The first symmetry group larger than U(1) is U(2) (with special
unitary part SU(2)). U(2) acts irreducibly on a 2-dimensional
complex space. Therefore we need at least **2 states** at M=1.

The minimum set: {(0,1), (1,1)} — two states at M=1.
These two states span a 2-dimensional complex space.
The symmetry group is SU(2).
SU(2) is not isomorphic to U(1). M=1 is non-self-similar to M=0. ✓

**At M=2:**
Following the same logic: the minimum set at M=2 that gives new
symmetry would need to span a space whose symmetry group is not
SU(2) or U(1).

But here is the key question: **what determines how many states
we take at M=2?**

**Decision Point 3b: Why doesn't M=2 give triplets?**

The token structure at M=2: tokens are [0^N 11 0] for N=0,1,2,...
These are perfectly valid tokens. Why can't we take {(0,2),(1,2),(2,2)}
— three M=2 states — and get SU(3)?

**This is the hardest decision point in the whole proof.**

Several candidate answers:

**Candidate answer 1:** M=2 states are not independent of M=1 states.

A token at M=2 is [0^N 11 0]. This contains two 1-bits. The first
1-bit already appeared at M=1. In some sense, M=2 is "M=1 plus one
more 1-bit." If we think of token construction as sequential — each
M-step adds one 1-bit — then M=2 states are not fundamentally new;
they are M=1 states with one additional 1-bit appended.

→ If this is right, M=2 does not give a new independent symmetry level.
The states at M=2 are constructively dependent on M=1.

**Is this rigorous?** Not yet. We need a precise definition of
"constructively dependent." This is what we need to formalize.

**Candidate answer 2:** The minimum spanning set argument.

At M=1, the minimum set giving new symmetry is 2 states.
At M=2, what is the minimum set giving symmetry not already in
{U(1), SU(2)}?

SU(3) needs 3 states. But we could also ask: is there a symmetry
group with dimension 2 that is not isomorphic to SU(2)?
Yes — U(2). But U(2) is SU(2) × U(1), which is a product of
symmetries already present. By minimality, we do not count
product symmetries as new.

So the first *genuinely new* symmetry beyond SU(2) is SU(3),
which needs dimension 3. But why does this happen at M=3 and
not M=2?

**This requires connecting M-value to dimension. That connection
is currently missing.**

**Candidate answer 3:** The 1-bit run structure forces it.

The M-run at M=k consists of k identical 1-bits. The symmetry
of k identical objects under linear transformations is:
- k=1: one 1-bit. The minimum non-trivial complex space containing
  one "marked" direction: dimension 2 (one marked, one reference).
- k=2: two 1-bits. These are indistinguishable (both are 1-bits).
  The space of indistinguishable pairs: symmetric square of ℂ².
  This is not a new fundamental space.
- k=3: three 1-bits, all identical. The complex space carrying
  a 3-dimensional representation... but why 3-dimensional?

**This candidate answer is suggestive but not rigorous yet.**

---

## Current Status: Where We Are Stuck

The M=0 → dimension 1 and M=1 → dimension 2 arguments are relatively clean.

The M=3 → dimension 3 argument has a genuine gap. We do not yet have
a derivation from token structure alone of why:
- M=2 is NOT a new symmetry level
- M=3 IS a new symmetry level with dimension 3

**The gap stated precisely:**

We need a function f: M → dimension(M) that:
1. Comes from the token structure (not from SM knowledge)
2. Gives f(0)=1, f(1)=2, f(3)=3
3. Explains why M=2 is not a new level

**Three paths forward:**

**Path A:** Define "constructive dependence" precisely and show
M=2 states are constructively dependent on M=1 states, while
M=3 states introduce genuine new structure.

**Path B:** Define the grouping by the structure of the M-run
(k identical 1-bits) and show the natural representation space
of k identical objects has dimension k for k=1 and k=3, but
reduces to lower dimensions for k=2.

**Path C:** Accept that M=2 may also be a symmetry level, with
some symmetry group, and the real claim is just that exactly
M=0,1,3 have *non-self-similar* symmetry groups among the
first few levels. Then prove the M≥4 self-similarity by the
SU(k) decomposition argument (which is solid).

**Path C is the most honest current position.**

Under Path C, the proof does not need to explain why M=2 is skipped.
It needs to show:
- M=0 gives U(1) — non-trivially shown
- M=1 gives SU(2) — non-self-similar to U(1) — shown
- M=2 gives... something. What?
- M=3 gives SU(3) — non-self-similar to SU(2) and U(1) — shown
- M≥4 gives no new non-self-similar structure — shown (solid)

**The honest list of what we still need for M=2:**
What symmetry group does M=2 give? Is it self-similar to M=1?
If yes, why?

---

## Next Steps

1. Formalize "constructive dependence" — try Path A.
2. If Path A fails to give a clean definition, try Path B.
3. If both fail, adopt Path C and be honest that M=2 is
   not yet fully characterized, but document what IS proven.
4. In any case, add the M≥4 self-similarity argument to
   proofs.md as a standalone proven result, since it is solid.

---

*This document is a working scratch pad, not a finished proof.
Every dead end is recorded. No path is abandoned silently.*
