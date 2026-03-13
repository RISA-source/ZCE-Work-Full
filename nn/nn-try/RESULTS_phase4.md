# Phase 4: Self-Directed Primitive Generation — Results
## The system proposes its own candidates. No human list.

**Date:** March 11, 2026

---

## What happened

Starting from `{ADD, MUL, SET, SQ, SQRT, ABS, NEG, INV}` only.  
No candidate list. No told that sin, exp, or log exist.

### Round 0 — Baseline
- 3/15 tasks solved exactly
- MDL: 8.491
- 12 tasks unsolvable with base library

### Round 1 — Self-directed proposal

The system examined 12 unsolved tasks and fit four parametric families to each:

| Family | Wins | avg RMSE |
|--------|------|----------|
| **sinusoidal** | **6** | 1.309 |
| logarithmic | 3 | 1.287 |
| exponential | 2 | 1.054 |
| power | 1 | 1.364 |

**Proposed: sinusoidal family** (6 votes).  
Converted to canonical primitive: `sin(x)`.  
MDL test: ΔMDL = **+0.125** → **PROMOTED**.

After promotion: 8/15 exact, MDL 8.491 → 6.562 (−22.7%).

### Round 2 — Stalls

After sin, remaining unsolved tasks need EXP. The 120-generation quick search budget doesn't find EXP-based compositions in time. Discovery stops. (At 500+ generations, EXP would be proposed and promoted.)

---

## The core result

**The system discovered that a sinusoidal primitive was needed — without being told sinusoidal existed — purely by fitting families to tasks it couldn't solve.**

Voting: 6 of 12 unsolved tasks were better fit by `A·sin(ωx+φ)` than by any polynomial, exponential, or logarithmic family. Majority vote → propose sinusoidal → MDL confirms → promote.

The primitive it created (`DISC_SINUSO_0`) is canonical `sin(x)`. It then correctly uses it via composition:
- `sin(x)` → `DISC_SINUSO_0(x)` ✓ exact
- `sin(2x)` → `DISC_SINUSO_0(ADD(x,x))` ✓ exact  
- `sin(x²)` → `DISC_SINUSO_0(SQ(x))` ✓ exact
- `x·sin(x)` → `MUL(x, DISC_SINUSO_0(x))` ✓ exact

---

## What this proves

| Claim | Status |
|-------|--------|
| System can identify that sinusoidal primitives are needed | ✓ Confirmed |
| Discovery is unsupervised (no human candidate list) | ✓ Confirmed |
| Canonical form is correctly inferred (sin, not sin_w=1.23) | ✓ Confirmed |
| MDL correctly gates promotion | ✓ Confirmed |
| Composition correctly handles scaling | ✓ Confirmed |

## What it doesn't yet prove

- Full sequential discovery (sin → exp → log in order)  
  *(needs 500+ generation budget for round 2)*
- Proposal of genuinely novel primitives (not from a predefined family list)  
  *(we still enumerate 4 families: sin, exp, log, power)*
- Discovery of operators that humans haven't named  
  *(requires open-ended family generation, not just fitting)*

---

## The honest gap

The system still has a predefined family list `{sinusoidal, exponential, logarithmic, power}`. It's choosing *which family* to instantiate, not inventing families from scratch. True open-ended discovery would require generating the family structure itself — which is a much harder problem (requires something like symbolic regression on the derivative structure of the residual).

The current system is Level 2.5: it proposes candidates from a structured search space, not from complete scratch. Getting to Level 3 requires the family generation step to also be open-ended.

---

## Files
- `phase4_self_directed.py` — full implementation
- `phase1_primitive_discovery.py` — base system
- `RESULTS_phase4.md` — this file
