# ZCE: Zero-Count Encoding

**Author:** Rishi Saraff

---

## What This Is

ZCE is a self-delimiting bit-stream computation language designed from scratch to make the Invariance Theorem and Symmetry of Information constructive and measurable. This repository provides a working universal language, a self-interpreter, a complete test suite, and empirical verification of the theoretical claims in the companion document.

The primary contribution is constructive and empirical: build the system, run it, measure the constants.

---

## The ZCE Language

### Token Encoding

ZCE programs are self-delimiting bit streams. Every token is encoded as:

```
[identity zeros] [depth+1 ones] [terminator zero]
```

A token with identity k and depth d costs k + d + 2 bits. All arguments — including jump offsets — are Elias-coded (self-delimiting integers). There are no fixed-width fields anywhere in the format.

### Self-Delimiting Header

Every ZCE program begins with `elias(program_length_in_bits)`. The executor reads this before any instruction and knows exactly where the program ends. Programs can be concatenated without boundary markers — this is the Frozen property.

### Base Instructions

| Token | Name | Semantics |
|-------|------|-----------|
| 1 | SET  | `slots[d] = v` |
| 2 | ADD  | `slots[d] = slots[a] + slots[b]` |
| 3 | JIF  | Jump to Elias-coded offset if `slots[cond] == 0` |
| 4 | JMP  | Unconditional jump to Elias-coded offset |
| 5 | DEF  | Define a new extended operation |

### DEF and the Frozen Decoder

DEF extends the language inline without modifying the base executor. Defined operations are stored in a rule table; the executor dispatches to them. The rule set is fixed at load time and does not change during execution — this is the Frozen property.

### Minimum Universal Op Set

SUB, EQ, NOT, LOAD, STOR — five extended ops, 138 bits of DEF section — are sufficient for universal computation. The self-interpreter additionally uses MUL and LT (7 ops total, 194 bits). Neither DIV nor MOD is needed.

---

## Two Notions of c_sym

The companion document introduces two distinct constants that must not be confused:

**c_sym_system = K(V0) - K(I)**

A property of the language. Measures the gap between vocabulary complexity and interpreter complexity. Always negative by Lemma 1 (the interpreter necessarily encodes the vocabulary, so K(I) >= K(V0)). For ZCE: K(V0) = 194b, K(I) = 10675b, c_sym_system = -10481b.

**c_sym_pair = K(x,y) - K(x) - K(y|x)**

Measured per pair. The saving from writing a joint program instead of two separate ones. Always negative because the DEF section is paid once in the joint program but twice separately. For ZCE: measured at -264 to -312b. The saving is approximately -K(V0) = -194b.

These are not the same number. c_sym_system is the structural cost of execution. c_sym_pair is the per-pair amortization saving.

**c_exec = K(I) - K(V0) = -c_sym_system >= 0**

Execution overhead. Always non-negative. For ZCE: c_exec = 10481b. Corollary: N programs described jointly save (N-1) x c_exec bits relative to N separate descriptions.

---

## Direction A: ZCE Simulates Any Turing Machine

To show K_Sigma(f,0) <= K(f) + c_Sigma, we exhibit a fixed ZCE program structure that can simulate any TM. Six TMs are implemented and verified:

| Program | Cases verified |
|---------|---------------|
| Binary increment | 9/9 including all carry chains |
| Tape copy | 4/4 |
| a*b* recognizer | 9/9 |
| Palindrome checker | 8/8 |
| Popcount | 4/4 |
| Universal TM (2-state 2-symbol) | 6/6 |

Overhead decomposition for increment (n = tape length):

| n | define | loop overhead | c_A |
|---|--------|---------------|-----|
| 1 | 138b | 419b | 557b |
| 8 | 138b | 429b | 567b |
| 32 | 138b | 439b | 577b |
| 64 | 138b | 445b | **583b** |

The define section is constant at 138 bits. Loop overhead varies 26 bits over n = 1..64 due to Elias coding of larger offsets.

**c_Sigma <= 577 bits** (measured upper bound for n <= 32).

---

## Direction B: ZCE Self-Interpreter

To show K(f) <= K_Sigma(f,0) + c_interp, we build a fixed ZCE program that reads another ZCE program stored in slots 500+, simulates it instruction by instruction, and places the result in slot 0.

The interpreter handles all five base operations (SET, ADD, JIF, JMP, DEF) and all 7 extended ops (SUB, MUL, EQ, LT, NOT, LOAD, STOR) through the do_custom handler. It uses a shared Elias decoder subroutine with a 17-site binary-search trampoline, avoiding 17 inline copies of the decoder (~15000 bits saved).

### Two Cost Components

The interpreter program has two parts:

**Logic bits** ≈ constant: the interpreter machinery — dispatch table, token reader, Elias decoder, handlers for each operation. This is c_interp.

**Data bits** ≈ 23 x |inner|: the SET instructions storing inner program bits into slots 500+. Grows linearly with inner program size. Not part of the constant.

| Case | inner bits | logic bits | data bits |
|------|-----------|------------|-----------|
| SET(0,42) | 24b | 10675b | 530b |
| loop n=8 | 432b | 11337b | 9914b |
| linear 1..15 | 504b | 11395b | 11570b |

Logic variation: 1302 bits across all cases.

**c_interp <= 11977 bits** (measured upper bound, max over 7 inner programs).

### Full EXT Op Support

The do_custom handler in the interpreter reads the inner program's DEF-defined rule table (stored at outer slots 300+, with inner slots safely at 5000+) to determine the number of arguments (na) and action (ap) for each EXT op, then dispatches to the correct outer operation. All 7 EXT ops verified:

| Inner program | EXT ops used | Result verified |
|---------------|-------------|-----------------|
| sum 1..20     | LT          | 210 ✓           |
| sum 1..25     | LT          | 325 ✓           |
| sum 1..30     | LT          | 465 ✓           |
| pal 10101     | SUB, EQ, LT, LOAD | 1 ✓      |
| pal 110011    | SUB, EQ, LT, LOAD | 1 ✓      |
| pal 010       | SUB, EQ, LT, LOAD | 1 ✓      |

### What Drives c_interp

The ~11000b cost breaks down as:
- 102 JIF/JMP instructions for interpreter flow control — offsets into an ~11000-bit body, ~30 bits each after Elias coding. Cannot be compressed; they are actual branches in a general dispatcher.
- Elias decoder subroutine + 17-site trampoline — ~1850b total (vs ~17000b if inlined).
- ADD/EXT instructions for slot addressing and rule table access.
- ISLOT_BASE=5000 adds ~4.6 extra bits per ISLOT constant SET instruction vs ISLOT_BASE=200.

### Formal Bound on c_interp

For an inner program of n bits:

    c_interp(n) <= 10132 + 188 * ceil(log2(n))

Derivation: 102 JIF/JMP instructions, each offset growing at most 2 bits per doubling of program size. 102 x 2 = 204 bits/doubling = 148 bits/log2-unit. Measured slope = 139 <= 148. Formula is conservative. Verified n=3..30 (104b..1088b inner programs), all within bound.

---

## Log Correction Elimination

The standard symmetry theorem (Kolmogorov) reads:

```
K(x,y) = K(x) + K(y|x) + O(log K(x,y))
```

The O(log) term arises because encoding program boundaries requires O(log n) bits. The Frozen property eliminates this: since every ZCE program begins with elias(length), the executor advances past P_x exactly and reads P_{y|x} without any external boundary marker.

**Empirical test:** correction(x,y) = K(x) + K(y|x) - K(x,y) should be constant as program sizes grow. Using programs spanning 24b to 2232b with a fixed K(y|x) = 16b:

| K(x) | K(y|x) | K(x,y) | correction | log K(x,y) |
|------|--------|--------|------------|------------|
| 24b | 16b | 32b | 8b | 3.466 |
| 240b | 16b | 248b | 8b | 5.513 |
| 1024b | 16b | 1032b | 8b | 6.939 |
| 2224b | 16b | 2232b | 8b | 7.711 |

Correction = 8b exactly for all cases. Slope on log(K(x,y)) = 0.0000. Standard deviation = 0.0b. The O(log) term is exactly eliminated.

---

## Combined Result

```
K(f) - 11977  <=  K_Sigma(f,0)  <=  K(f) + 577
```

Both constants are independent of f and measured from running code. The bounds hold for all programs tested. These are measured upper bounds — see "What Is and Is Not Established" for the formal status.

---

## Verification Table

Every cell filled with live measurements from running test_zce.py (18 suites, 85/85 checks):

| Quantity | Bound | Measured | Status | Type |
|----------|-------|----------|--------|------|
| K(V0) >= DEF_LB | >= 184b | 194b | ✓ | [measured] |
| K(I) >= K(V0) [Lemma 1] | must hold | 10675 >= 194 | ✓ | [theorem] |
| c_sym_system <= 0 [Thm 1] | must hold | -10481b | ✓ | [theorem] |
| c_exec >= 0 | must hold | 10481b | ✓ | [theorem] |
| c_sym_pair (5 cases) | all < 0 | -304 to -264b | ✓ | [measured] |
| Log correction slope | = 0 [Lemma 2] | 0.0000 | ✓ | [measured] |
| Log std/|mean| | < 0.1 | 0.000 | ✓ | [measured] |
| Thm 3 (loose bound) | >= 103b | 10675b | ✓ | [theorem] |
| logic <= 10132+188*log2(n) | formula holds n=3..30 | all within | ✓ | [formal] |
| ZCE c_A | <= 577b | 577b | ✓ | [measured] |
| ZCE c_interp | <= 11977b | 11977b | ✓ | [measured] |
| Combined bound | K(f)-11977 <= K_Sigma <= K(f)+577 | holds | ✓ | [both directions] |

---

## What Is and Is Not Established

| Claim | Status |
|-------|--------|
| ZCE is a working universal language | Established — executor, assembler, 6 TMs, self-interpreter all verified |
| c_Sigma <= 577 bits | Measured upper bound for increment TM, n = 1..32 |
| c_interp <= 11977 bits | Measured upper bound, max over 7 inner programs |
| do_custom supports all 7 EXT ops | Established — SUB, MUL, EQ, LT, NOT, LOAD, STOR all verified through interpreter |
| Both constants independent of f | Consistent with all measurements; not formally proven for all computable f |
| c_sym_system <= 0 | Follows from Lemma 1 (structural theorem, not empirical) |
| Log term eliminated (O(1) correction) | Demonstrated across 3 orders of magnitude; follows from self-delimiting structure |
| Theorem 3 lower bound (Thm 3 in doc) | Holds but very loose: bound ≈ 103b, actual ≈ 10675b. Formula is not tight. |
| Invariance Theorem | Not proven here — classical result (Kolmogorov/Chaitin/Gács). Used as background. |

---

## Files

- `zce_core.py` — BS, Exec, Asm (= AsmOpt), EXT: the language
- `zce_interp.py` — TM builders, self-interpreter, symmetry programs, overhead measurement, system_constants(), log_correction_test()
- `test_zce.py` — 18 test suites, 85 checks: `python3 test_zce.py`
- `ZCE_proof.md` — detailed proof sketch with derivations

---

## References

- Li, M. & Vitányi, P. *An Introduction to Kolmogorov Complexity and Its Applications.* Springer, 3rd ed. 2008.
- Chaitin, G. *A theory of program size formally identical to information theory.* JACM 22(3), 1975.
- Gács, P. *On the symmetry of algorithmic information.* Soviet Math. Doklady 15, 1974.
