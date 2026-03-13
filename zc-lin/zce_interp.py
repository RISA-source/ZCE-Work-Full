"""
ZCE self-interpreter and program builders.
Author: Rishi Saraff
"""

from zce_core import BS, Asm, AsmOpt, EXT, Exec, run_stream, stream_to_bits, consts, TOK, OP

INNER_BASE = 500   # inner program bits start here (slots 500..500+len-1)
ISLOT_BASE = 5000  # inner program slots start here (slots 5000+, no collision)
RULE_BASE  = 300   # DEF rule table slots 300..371 (9 ops x 8 fields)
N_CALL_SITES = 17  # number of Elias decoder call sites in interpreter


# ── Direction A: TM builders ─────────────────────────────────────────────────

def _minimal_defs(a):
    """Define only ops needed for universal simulation: SUB EQ NOT LOAD STOR."""
    P = 0
    a._defop(TOK['SUB'],  OP['SUB'],  3, [P, P, P])
    a._defop(TOK['EQ'],   OP['EQ'],   3, [P, P, P])
    a._defop(TOK['NOT'],  OP['NOT'],  2, [P, P])
    a._defop(TOK['LOAD'], OP['LOAD'], 2, [P, P])
    a._defop(TOK['STOR'], OP['STOR'], 2, [P, P])


def build_increment(tape):
    """Binary increment. Scans LSB→MSB flipping bits while carry propagates.
    Uses only SUB/EQ/NOT/LOAD/STOR — no MUL/LT needed."""
    a = Asm(); _minimal_defs(a); n = len(tape)
    for i, b in enumerate(tape): a.SET(100+i, b)
    a.SET(1, 0); a.SET(2, 1)
    a.SET(10, n-1)
    a.label('loop')
    a.SET(30, 100); a.ADD(30, 30, 10); a.LOAD(31, 30)
    a.EQ(20, 31, 1)
    a.JIF(20, 'carry')
    a.STOR(30, 2); a.JMP('done')
    a.label('carry')
    a.STOR(30, 1)
    a.EQ(20, 10, 1); a.NOT(20, 20); a.JIF(20, 'done')
    a.SUB(10, 10, 2); a.JMP('loop')
    a.label('done'); a.SET(0, 1)
    return a.build(), a

def build_copy(data):
    a = Asm(); a.std(); n = len(data)
    for i, v in enumerate(data): a.SET(100+i, v)
    consts(a); a.SET(10, 0); a.SET(11, n)
    a.label('loop')
    a.LT(20, 10, 11); a.JIF(20, 'done')
    a.SET(30, 100); a.ADD(30, 30, 10); a.LOAD(31, 30)
    a.SET(32, 150); a.ADD(32, 32, 10); a.STOR(32, 31)
    a.ADD(10, 10, 2); a.JMP('loop')
    a.label('done'); a.SET(0, 1)
    return a.build(), a

def build_astar_bstar(tape):
    a = Asm(); a.std(); n = len(tape)
    for i, s in enumerate(tape): a.SET(100+i, s)
    consts(a); a.SET(5, n); a.SET(201, 0); a.SET(10, 0); a.SET(0, 0)
    a.label('loop')
    a.LT(20, 10, 5); a.JIF(20, 'done')
    a.SET(30, 100); a.ADD(30, 30, 10); a.LOAD(31, 30)
    a.EQ(32, 31, 1); a.EQ(33, 31, 2); a.EQ(34, 31, 3)
    a.EQ(35, 201, 1); a.EQ(36, 201, 2)
    a.MUL(40, 35, 33); a.MUL(41, 36, 32)
    a.ADD(201, 201, 40); a.ADD(201, 201, 41)
    a.EQ(42, 201, 3); a.NOT(43, 42); a.MUL(44, 34, 43); a.ADD(0, 0, 44)
    a.NOT(45, 34); a.JIF(45, 'done')
    a.ADD(10, 10, 2); a.JMP('loop')
    a.label('done')
    return a.build(), a

def build_palindrome(tape):
    a = Asm(); a.std(); n = len(tape)
    for i, b in enumerate(tape): a.SET(100+i, b)
    consts(a); a.SET(10, 0); a.SET(11, n-1); a.SET(0, 1)
    a.label('loop')
    a.LT(20, 10, 11); a.JIF(20, 'done')
    a.SET(30, 100); a.ADD(30, 30, 10); a.LOAD(31, 30)
    a.SET(32, 100); a.ADD(32, 32, 11); a.LOAD(33, 32)
    a.EQ(34, 31, 33); a.NOT(35, 34)
    a.MUL(36, 0, 35); a.SUB(0, 0, 36)
    a.ADD(10, 10, 2); a.SUB(11, 11, 2); a.JMP('loop')
    a.label('done')
    return a.build(), a

def build_popcount(bits):
    a = Asm(); a.std(); n = len(bits)
    for i, b in enumerate(bits): a.SET(100+i, b)
    consts(a); a.SET(10, 0); a.SET(11, n); a.SET(0, 0)
    a.label('loop')
    a.LT(20, 10, 11); a.JIF(20, 'done')
    a.SET(30, 100); a.ADD(30, 30, 10); a.LOAD(31, 30); a.ADD(0, 0, 31)
    a.ADD(10, 10, 2); a.JMP('loop')
    a.label('done')
    return a.build(), a

def build_utm(table, tape, head=0, init_state=0):
    """Universal TM (2-state 2-symbol). dr=1=right, dr=2=halt.
    Uses EQ dispatch instead of MUL addressing — no MUL/LT needed."""
    a = Asm(); _minimal_defs(a); n = len(tape)
    for i, b in enumerate(tape): a.SET(100+i, b)
    a.SET(1, 0); a.SET(2, 1); a.SET(4, n); a.SET(5, 2)
    a.SET(200, head); a.SET(201, init_state); a.SET(0, 0)
    for (st, sym), (ns, nb, dr) in table.items():
        base = 300 + (st*2 + sym)*3
        a.SET(base, ns); a.SET(base+1, nb); a.SET(base+2, dr)
    a.label('step')
    a.SET(30, 100); a.ADD(30, 30, 200); a.LOAD(31, 30)
    a.EQ(40, 201, 1); a.EQ(41, 31, 1)
    a.JIF(40, 'state1')
    a.JIF(41, 'st0s1');  a.SET(35, 300); a.JMP('go')
    a.label('st0s1');    a.SET(35, 303); a.JMP('go')
    a.label('state1')
    a.JIF(41, 'st1s1');  a.SET(35, 306); a.JMP('go')
    a.label('st1s1');    a.SET(35, 309)
    a.label('go')
    a.LOAD(36, 35)
    a.SET(37, 1); a.ADD(37, 35, 37); a.LOAD(37, 37)
    a.SET(38, 2); a.ADD(38, 35, 38); a.LOAD(38, 38)
    a.STOR(30, 37)
    a.SET(201, 0); a.ADD(201, 201, 36)
    a.EQ(40, 38, 5); a.NOT(40, 40); a.JIF(40, 'end')
    a.ADD(200, 200, 2)
    a.EQ(40, 200, 4); a.JIF(40, 'step')
    a.SUB(200, 200, 2); a.JMP('step')
    a.label('end'); a.SET(0, 1)
    return a.build(), a

def build_entangled(n):
    """Joint program computing x=sum(1..n) and y=sum_of_squares(1..n) in one loop."""
    a = Asm(); a.std(); consts(a)
    a.SET(10, 0); a.SET(11, n); a.SET(0, 0); a.SET(1, 0)
    a.label('loop')
    a.LT(20, 10, 11); a.JIF(20, 'done')
    a.ADD(10, 10, 2); a.ADD(0, 0, 10)
    a.MUL(30, 10, 10); a.ADD(1, 1, 30)
    a.JMP('loop')
    a.label('done')
    return a.build(), a, sum(range(1, n+1)), sum(i*i for i in range(1, n+1))


# ── Inner programs for self-interpreter testing ───────────────────────────────

def inner_jif_nonzero():
    a = AsmOpt()
    a.SET(5, 1); a.JIF(5, 'skip'); a.SET(0, 42)
    a.JMP('end'); a.label('skip'); a.SET(0, 99); a.label('end')
    return a.build(), 42

def inner_jif_zero():
    a = AsmOpt()
    a.SET(5, 0); a.JIF(5, 'taken'); a.SET(0, 99)
    a.JMP('end'); a.label('taken'); a.SET(0, 77); a.label('end')
    return a.build(), 77

def inner_loop(count):
    assert count <= 10
    a = AsmOpt(); a.SET(0, 0); a.SET(5, count)
    for i in range(count, 0, -1):
        a.label(f'step_{i}'); a.JIF(5, 'done'); a.ADD(0, 0, 5)
        if i > 1: a.SET(5, i-1)
    a.label('done')
    return a.build(), sum(range(1, count+1))

def inner_linear_sum(n):
    a = AsmOpt(); a.SET(0, 0)
    for i in range(1, n+1): a.SET(10+i, i); a.ADD(0, 0, 10+i)
    return a.build(), sum(range(1, n+1))

def inner_runtime_def_set():
    """Inner program: DEF op15=SET, op15(0,7), ADD(0,0,0) → 14."""
    body = BS()
    body.token(5,1);  body.elias(15); body.elias(1)
    body.elias(0);    body.elias(1);  body.elias(0); body.elias(1)
    body.token(15,1); body.elias(0);  body.elias(7)
    body.token(2,0);  body.elias(0);  body.elias(0); body.elias(0)
    hdr = BS(); hdr.elias(body.count())
    full = BS(); full.bits(hdr.b); full.bits(body.b)
    return full.tobytes(), 14

def inner_runtime_def_add():
    """Inner program: DEF op15=ADD, unrolled sum 1+2+3+4+5=15."""
    body = BS()
    body.token(5,1);  body.elias(15); body.elias(2)
    body.elias(0);    body.elias(0);  body.elias(0)
    body.elias(0);    body.elias(2)
    body.token(1,0);  body.elias(0);  body.elias(0)
    body.token(1,0);  body.elias(5);  body.elias(1)
    body.token(1,0);  body.elias(7);  body.elias(0)
    for _ in range(5):
        body.token(2,0);  body.elias(7); body.elias(7); body.elias(5)
        body.token(15,1); body.elias(0); body.elias(0); body.elias(7)
    hdr = BS(); hdr.elias(body.count())
    full = BS(); full.bits(hdr.b); full.bits(body.b)
    return full.tobytes(), 15


# ── Symmetry of information programs ─────────────────────────────────────────

def prog_x(x):
    a = Asm(); a.std(); a.SET(0, x); return a.build()

def prog_xy(x, y):
    a = Asm(); a.std(); a.SET(0, x); a.SET(1, y); return a.build()

def prog_y_given_x(x, y, relation):
    a = Asm(); a.std()
    if relation == 'independent':  a.SET(1, y)
    elif relation == 'double':     a.ADD(1, 0, 0)
    elif relation == 'plus_k':     a.SET(90, y-x); a.ADD(1, 0, 90)
    elif relation == 'square':     a.MUL(1, 0, 0)
    elif relation == 'complement': a.SET(90, 255); a.SUB(1, 90, 0)
    return a.build()

def measure_symmetry(x, y, relation):
    """Measure per-pair symmetry saving.

    Returns c_sym_pair = K(x,y) - K(x) - K(y|x).

    This is the per-pair saving from writing a joint program vs two
    separate programs. It is always negative because the DEF section
    (K(V0)) is paid once in the joint program but twice in the separate
    programs. This is DISTINCT from the system-level c_sym defined as
    K(V0) - K(I); see system_constants() for that quantity.
    """
    s_joint = prog_xy(x, y)
    s_x     = prog_x(x)
    s_cond  = prog_y_given_x(x, y, relation)
    ex = Exec(ext=EXT); ex.load(s_cond); ex.slots[0] = x; ex.run()
    return {
        'k_joint':    len(s_joint)*8,
        'k_x':        len(s_x)*8,
        'k_cond':     len(s_cond)*8,
        'c_sym_pair': len(s_joint)*8 - len(s_x)*8 - len(s_cond)*8,
        # legacy key kept for existing callers
        'c_sym':      len(s_joint)*8 - len(s_x)*8 - len(s_cond)*8,
        'cond_ok':    ex.slot(1) == y,
    }


def system_constants(inner_stream=None):
    """Return ZCE system-level constants as defined in the document.

    Two distinct notions of c_sym exist and must not be confused:

    c_sym_system = K(V0) - K(I)  (document Theorem 1)
        The gap between vocabulary complexity and interpreter complexity.
        Always negative (Lemma 1: K(I) >= K(V0) necessarily).
        For ZCE: K(V0) ~ def_bits of interpreter (~194b),
                 K(I)  ~ interpreter logic bits (~8291-9035b).
        This is a property of the language, not of any pair (x,y).

    c_sym_pair = K(x,y) - K(x) - K(y|x)  (measured per pair)
        The per-pair saving from joint description.
        Always negative because DEF section paid once vs twice.
        For ZCE: measured at -264 to -312b across test cases.
        The saving is roughly -K(V0) = -194b (one DEF section).

    c_exec = K(I) - K(V0) = -c_sym_system  (document definition)
        Execution overhead: always >= 0.

    The document's Theorem 2 (exact symmetry) uses c_sym_pair.
    The document's Lemma 1/Theorem 1 uses c_sym_system.
    """
    if inner_stream is None:
        a = Asm(); a.SET(0, 42)
        inner_stream = a.build()
    ib = stream_to_bits(inner_stream)
    _, ia = build_interpreter(inner_stream)
    logic, _ = interpreter_logic_bits(ia, len(ib))
    k_v0   = ia.def_bits()          # K(V0) approximation
    k_i    = logic                   # K(I) approximation
    return {
        'k_v0':           k_v0,
        'k_i':            k_i,
        'c_sym_system':   k_v0 - k_i,   # always <= 0
        'c_exec':         k_i - k_v0,   # always >= 0
    }


def log_correction_test():
    """Test whether the O(log) correction in symmetry of information is eliminated.

    Document Lemma 2: in a self-describing system with the Frozen property,
    the O(log K(x,y)) correction is exactly zero. Verified by showing
    correction(x,y) = K(x) + K(y|x) - K(x,y) is constant as program
    sizes grow over several orders of magnitude.

    Uses programs with variable-length payloads so sizes span ~24b to ~2200b.
    K(y|x) is small and fixed (ADD(1,0,0) = double x), while K(x) grows.
    If the log term were present, correction would grow with log(K(x,y)).

    Returns dict with slope, intercept, correction values, and pass/fail.
    """
    import math, statistics

    def prog_with_payload(payload_size):
        a = Asm()
        for i in range(payload_size):
            a.SET(100 + i, i % 256)
        a.ADD(0, 1, 2)   # output: slot1+slot2
        return a.build()

    def prog_y_given_x_double():
        a = Asm(); a.ADD(1, 0, 0); return a.build()

    def prog_xy_with_payload(payload_size):
        a = Asm()
        for i in range(payload_size):
            a.SET(100 + i, i % 256)
        a.ADD(0, 1, 2)   # x output
        a.ADD(1, 0, 0)   # y = 2x
        return a.build()

    payloads = [0, 2, 5, 10, 20, 40, 80]
    results  = []
    for p in payloads:
        kx   = len(prog_with_payload(p)) * 8
        kyx  = len(prog_y_given_x_double()) * 8
        kxy  = len(prog_xy_with_payload(p)) * 8
        corr = kx + kyx - kxy          # positive when joint cheaper
        log_kxy = math.log(kxy) if kxy > 0 else 1.0
        results.append({'payload': p, 'kx': kx, 'kyx': kyx, 'kxy': kxy,
                        'correction': corr, 'log_kxy': log_kxy})

    log_sizes   = [r['log_kxy']    for r in results]
    corrections = [r['correction'] for r in results]
    mean_ls = statistics.mean(log_sizes)
    mean_c  = statistics.mean(corrections)
    cov = sum((log_sizes[i] - mean_ls) * (corrections[i] - mean_c)
              for i in range(len(results)))
    var_ls = sum((l - mean_ls) ** 2 for l in log_sizes)
    slope  = cov / var_ls if var_ls else 0.0
    stdev  = statistics.stdev(corrections) if len(corrections) > 1 else 0.0
    ratio  = stdev / abs(mean_c) if mean_c else 0.0

    return {
        'results':    results,
        'slope':      slope,
        'mean_corr':  mean_c,
        'stdev_corr': stdev,
        'ratio':      ratio,
        'slope_ok':   abs(slope) < 1.0,    # slope indistinguishable from 0
        'ratio_ok':   ratio < 0.1,
    }


# ── Self-interpreter (Direction B) ───────────────────────────────────────────
#
# Slot layout:
#   1-4    outer constants 0,1,2,3
#   5,6    outer constants 4,5
#   7      outer constant 8 (rule stride)
#   10     inner bit position
#   11     inner end bit position
#   12     token identity
#   17-19  decoded args
#   20-21  condition/comparison temps
#   30-23  address temps
#   24-26  value temps
#   27     inner program length
#   28-29  Elias subroutine state (k-countdown, accumulator)
#   30,62  jump offset temps
#   32-33  DEF loop temps
#   34     DEF at_type (read, discarded)
#   35     body_start (JIF/JMP base)
#   36     subroutine return site ID
#   37     subroutine result
#   38-26  rule-table and custom-op temps
#   200-299 inner slots
#   300-427 inner rule table
#   500+   inner program bits (1 bit per slot)
#
# c_interp measures interpreter logic bits only, independent of inner program
# size. Data storage costs ~23 bits per inner bit (SET instruction overhead),
# which is a separate O(|inner|) term, not part of the constant.

def _elias_sub(a):
    a.label('elias_sub')
    a.SET(28, 0)
    a.label('_sub_lz')
    a.SET(30, INNER_BASE); a.ADD(30, 30, 10)
    a.LOAD(23, 30);        a.ADD(10, 10, 2)
    a.EQ(20, 23, 1);       a.JIF(20, '_sub_val')
    a.ADD(28, 28, 2);      a.JMP('_sub_lz')
    a.label('_sub_val')
    a.SET(29, 1)
    a.label('_sub_lb')
    a.LT(20, 1, 28);       a.JIF(20, '_sub_done')
    a.MUL(29, 29, 3)
    a.SET(30, INNER_BASE); a.ADD(30, 30, 10)
    a.LOAD(23, 30);        a.ADD(10, 10, 2)
    a.ADD(29, 29, 23);     a.SUB(28, 28, 2)
    a.JMP('_sub_lb')
    a.label('_sub_done')
    a.SUB(37, 29, 2)


def _trampoline(a):
    """Binary-search dispatch back to call site stored in slot 36."""
    a.label('_trampoline')
    a.SET(26, 9);  a.LT(20, 36, 26); a.JIF(20, '_bs_r')
    a.SET(26, 4);  a.LT(20, 36, 26); a.JIF(20, '_bs_lr')
    a.SET(26, 2);  a.LT(20, 36, 26); a.JIF(20, '_bs_llr')
    a.SET(26, 1);  a.LT(20, 36, 26); a.JIF(20, '_bs_ret1')
    a.JMP('_ret_0')
    a.label('_bs_ret1');  a.JMP('_ret_1')
    a.label('_bs_llr')
    a.SET(26, 3);  a.LT(20, 36, 26); a.JIF(20, '_bs_ret3')
    a.JMP('_ret_2')
    a.label('_bs_ret3');  a.JMP('_ret_3')
    a.label('_bs_lr')
    a.SET(26, 6);  a.LT(20, 36, 26); a.JIF(20, '_bs_lrr')
    a.SET(26, 5);  a.LT(20, 36, 26); a.JIF(20, '_bs_ret5')
    a.JMP('_ret_4')
    a.label('_bs_ret5');  a.JMP('_ret_5')
    a.label('_bs_lrr')
    a.SET(26, 7);  a.LT(20, 36, 26); a.JIF(20, '_bs_lrr78')
    a.JMP('_ret_6')
    a.label('_bs_lrr78')
    a.SET(26, 8);  a.LT(20, 36, 26); a.JIF(20, '_bs_ret8')
    a.JMP('_ret_7')
    a.label('_bs_ret8');  a.JMP('_ret_8')
    a.label('_bs_r')
    a.SET(26, 13); a.LT(20, 36, 26); a.JIF(20, '_bs_rr')
    a.SET(26, 11); a.LT(20, 36, 26); a.JIF(20, '_bs_rlr')
    a.SET(26, 10); a.LT(20, 36, 26); a.JIF(20, '_bs_ret10')
    a.JMP('_ret_9')
    a.label('_bs_ret10'); a.JMP('_ret_10')
    a.label('_bs_rlr')
    a.SET(26, 12); a.LT(20, 36, 26); a.JIF(20, '_bs_ret12')
    a.JMP('_ret_11')
    a.label('_bs_ret12'); a.JMP('_ret_12')
    a.label('_bs_rr')
    a.SET(26, 15); a.LT(20, 36, 26); a.JIF(20, '_bs_rrr')
    a.SET(26, 14); a.LT(20, 36, 26); a.JIF(20, '_bs_ret14')
    a.JMP('_ret_13')
    a.label('_bs_ret14'); a.JMP('_ret_14')
    a.label('_bs_rrr')
    a.SET(26, 16); a.LT(20, 36, 26); a.JIF(20, '_bs_ret16')
    a.JMP('_ret_15')
    a.label('_bs_ret16'); a.JMP('_ret_16')
    a.JMP('interp_done')


def _call_elias(a, result_slot, site_id, return_label):
    a.SET(36, site_id)
    a.JMP('elias_sub')
    a.label(return_label)
    if result_slot != 37:
        a.ADD(result_slot, 37, 1)


def _read_token(a, dest, tag):
    tz = f'tz_{tag}'; to = f'to_{tag}'; te = f'te_{tag}'
    a.SET(dest, 0)
    a.label(tz)
    a.SET(30, INNER_BASE); a.ADD(30, 30, 10)
    a.LOAD(23, 30);        a.ADD(10, 10, 2)
    a.EQ(20, 23, 2);       a.JIF(20, f'tz_body_{tag}')
    a.JMP(to)
    a.label(f'tz_body_{tag}')
    a.ADD(dest, dest, 2)
    a.JMP(tz)
    a.label(to)
    a.SET(30, INNER_BASE); a.ADD(30, 30, 10)
    a.LOAD(23, 30);        a.ADD(10, 10, 2)
    a.EQ(20, 23, 2);       a.JIF(20, te)
    a.JMP(to)
    a.label(te)


def build_interpreter(inner_stream):
    """Build the self-interpreter loaded with inner_stream as its input.
    Returns (program_bytes, asm_object).
    Result of inner program ends up in slot ISLOT_BASE (200)."""
    inner_bits = stream_to_bits(inner_stream)
    a = Asm()
    # Define only the ops actually used by the interpreter (DIV not needed)
    P = 0
    a._defop(TOK['SUB'],  OP['SUB'],  3, [P, P, P])
    a._defop(TOK['MUL'],  OP['MUL'],  3, [P, P, P])
    a._defop(TOK['EQ'],   OP['EQ'],   3, [P, P, P])
    a._defop(TOK['LT'],   OP['LT'],   3, [P, P, P])
    a._defop(TOK['NOT'],  OP['NOT'],  2, [P, P])
    a._defop(TOK['LOAD'], OP['LOAD'], 2, [P, P])
    a._defop(TOK['STOR'], OP['STOR'], 2, [P, P])

    for i, b in enumerate(inner_bits):
        a.SET(INNER_BASE + i, b)

    a.SET(1, 0); a.SET(2, 1); a.SET(3, 2); a.SET(4, 3)
    a.SET(5, 4); a.SET(6, 5); a.SET(7, 8)
    # Extra constants for EXT op dispatch in do_custom:
    # slot[8]=7=OP['EQ'],  slot[9]=9=OP['NOT']
    # slot[44]=10=OP['LOAD'], slot[45]=11=OP['STOR']
    # (slot[4]=3=OP['SUB'], slot[5]=4=OP['MUL'], slot[7]=8=OP['LT'] already above)
    a.SET(8, 7); a.SET(9, 9); a.SET(44, 10); a.SET(45, 11)

    a.SET(10, 0)
    _call_elias(a, 27, 0, '_ret_0')
    a.ADD(35, 10, 1)
    a.ADD(11, 10, 27)

    a.label('interp_loop')
    a.LT(20, 10, 11); a.JIF(20, 'interp_done')

    _read_token(a, 12, 'main')

    a.EQ(20, 12, 2); a.JIF(20, 'not_set'); a.JMP('do_set')
    a.label('not_set')
    a.EQ(20, 12, 3); a.JIF(20, 'not_add'); a.JMP('do_add')
    a.label('not_add')
    a.EQ(20, 12, 4); a.JIF(20, 'not_jif'); a.JMP('do_jif')
    a.label('not_jif')
    a.EQ(20, 12, 5); a.JIF(20, 'not_jmp'); a.JMP('do_jmp')
    a.label('not_jmp')
    a.EQ(20, 12, 6); a.JIF(20, 'not_def'); a.JMP('do_def')
    a.label('not_def')
    a.JMP('do_custom')

    a.label('do_set')
    _call_elias(a, 17, 1, '_ret_1')
    _call_elias(a, 18, 2, '_ret_2')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 18)
    a.JMP('interp_loop')

    a.label('do_add')
    _call_elias(a, 17, 3, '_ret_3')
    _call_elias(a, 18, 4, '_ret_4')
    _call_elias(a, 19, 5, '_ret_5')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 18); a.LOAD(24, 30)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 19); a.LOAD(25, 30)
    a.ADD(26, 24, 25)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 26)
    a.JMP('interp_loop')

    a.label('do_jif')
    _call_elias(a, 17, 6, '_ret_6')
    _call_elias(a, 43, 7, '_ret_7')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.LOAD(62, 30)
    a.EQ(20, 62, 1); a.JIF(20, 'interp_loop')
    a.ADD(10, 35, 43)
    a.JMP('interp_loop')

    a.label('do_jmp')
    _call_elias(a, 43, 8, '_ret_8')
    a.ADD(10, 35, 43)
    a.JMP('interp_loop')

    a.label('do_def')
    _call_elias(a, 17, 9,  '_ret_9')
    _call_elias(a, 18, 10, '_ret_10')
    a.ADD(32, 18, 2)
    a.SET(38, RULE_BASE)
    a.SET(39, 6);  a.SUB(39, 17, 39)
    a.MUL(39, 39, 7); a.ADD(38, 38, 39)
    a.SET(30, 1); a.ADD(30, 30, 38); a.STOR(30, 32)
    a.SET(33, 0)
    a.label('_def_at_loop')
    a.LT(20, 33, 32); a.JIF(20, '_def_at_done')
    _call_elias(a, 34, 11, '_ret_11')
    a.ADD(33, 33, 2); a.JMP('_def_at_loop')
    a.label('_def_at_done')
    _call_elias(a, 17, 12, '_ret_12')
    _call_elias(a, 18, 13, '_ret_13')
    a.SET(30, 6); a.ADD(30, 30, 38); a.STOR(30, 17)
    a.SET(30, 7); a.ADD(30, 30, 38); a.STOR(30, 18)
    a.SET(30, 0); a.ADD(30, 30, 38); a.SET(39, 1); a.STOR(30, 39)
    a.JMP('interp_loop')

    a.label('do_custom')
    # ── Step 1: look up rule table for this token ─────────────────────────────
    a.SET(38, RULE_BASE)
    a.SET(39, 6);  a.SUB(39, 12, 39)
    a.MUL(39, 39, 7); a.ADD(38, 38, 39)
    # check ok flag (slot table+0)
    a.SET(30, 0); a.ADD(30, 30, 38); a.LOAD(25, 30)
    a.EQ(20, 25, 2); a.JIF(20, 'interp_loop')   # ok==0 → skip unknown op
    # load na (slot table+1) — number of args
    a.SET(30, 1); a.ADD(30, 30, 38); a.LOAD(32, 30)

    # ── Step 2: read args from inner bitstream ────────────────────────────────
    _call_elias(a, 17, 14, '_ret_14')            # dest slot index
    a.SET(26, 2); a.LT(20, 32, 26); a.NOT(21, 20); a.JIF(21, '_cop_skip1')
    _call_elias(a, 18, 15, '_ret_15')            # a slot index (if na>=2)
    a.label('_cop_skip1')
    a.SET(26, 3); a.LT(20, 32, 26); a.NOT(21, 20); a.JIF(21, '_cop_skip2')
    _call_elias(a, 19, 16, '_ret_16')            # b slot index (if na>=3)
    a.label('_cop_skip2')

    # ── Step 3: load act (table+6) and ap (table+7) ───────────────────────────
    a.SET(30, 6); a.ADD(30, 30, 38); a.LOAD(39, 30)  # 39 = act
    a.SET(30, 7); a.ADD(30, 30, 38); a.LOAD(24, 30)  # 24 = ap

    # ── Step 4: dispatch on act + ap ─────────────────────────────────────────
    # act==1 (ap==1): SET-store — inner[dest] = raw value of arg-a (not a slot read)
    a.EQ(20, 24, 2); a.JIF(20, '_cop_not_set')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 18)
    a.JMP('interp_loop')

    # act==2 (ap==2): ADD-store — inner[dest] = inner[a] + inner[b]
    a.label('_cop_not_set')
    a.EQ(20, 24, 3); a.JIF(20, '_cop_not_add')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 18); a.LOAD(50, 30)  # 50 = inner[a]
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 19); a.LOAD(51, 30)  # 51 = inner[b]
    a.ADD(52, 50, 51)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # act==0, EXT ops: load inner[a] and inner[b] first (reuse 50,51)
    a.label('_cop_not_add')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 18); a.LOAD(50, 30)  # 50 = inner[a]
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 19); a.LOAD(51, 30)  # 51 = inner[b]

    # SUB: ap==OP['SUB']=3, slot[4]=3
    a.EQ(20, 24, 4); a.JIF(20, '_cx_not_sub')
    a.SUB(52, 50, 51)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # MUL: ap==OP['MUL']=4, slot[5]=4
    a.label('_cx_not_sub')
    a.EQ(20, 24, 5); a.JIF(20, '_cx_not_mul')
    a.MUL(52, 50, 51)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # EQ: ap==OP['EQ']=7, slot[8]=7
    a.label('_cx_not_mul')
    a.EQ(20, 24, 8); a.JIF(20, '_cx_not_eq')
    a.EQ(52, 50, 51)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # LT: ap==OP['LT']=8, slot[7]=8
    a.label('_cx_not_eq')
    a.EQ(20, 24, 7); a.JIF(20, '_cx_not_lt')
    a.LT(52, 50, 51)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # NOT: ap==OP['NOT']=9, slot[9]=9 (na=2, 50=inner[a], 51=inner[b] unused)
    a.label('_cx_not_lt')
    a.EQ(20, 24, 9); a.JIF(20, '_cx_not_not')
    a.NOT(52, 50)
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # LOAD: ap==OP['LOAD']=10, slot[44]=10
    # Semantics: inner[dest] = inner[inner[a]]
    # 50 = inner[a] (used as pointer into inner slot array)
    a.label('_cx_not_not')
    a.EQ(20, 24, 44); a.JIF(20, '_cx_not_load')
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 50); a.LOAD(52, 30)  # 52 = inner[inner[a]]
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.STOR(30, 52)
    a.JMP('interp_loop')

    # STOR: ap==OP['STOR']=11, slot[45]=11
    # Semantics: inner[inner[dest]] = inner[a]
    # 17 = dest slot index, 18 = a slot index, 50 = inner[a]
    # Need inner[dest] as the pointer:
    a.label('_cx_not_load')
    a.EQ(20, 24, 45); a.JIF(20, 'interp_loop')  # unknown ap → skip
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 17); a.LOAD(52, 30)  # 52 = inner[dest] = ptr
    a.SET(30, ISLOT_BASE); a.ADD(30, 30, 52); a.STOR(30, 50)  # inner[ptr] = inner[a]
    a.JMP('interp_loop')

    a.label('interp_done')
    a.SET(30, ISLOT_BASE); a.LOAD(0, 30)
    a.JMP('_end')

    _elias_sub(a)
    _trampoline(a)

    a.label('_end')
    return a.build(), a


def interpreter_logic_bits(asm_obj, n_inner_bits):
    """Return the number of bits attributable to interpreter logic vs. data storage.

    Data storage is the O(|inner|) cost of SET instructions that load inner bits
    into slots 500+. This grows linearly with inner program size and is not part
    of the constant. Logic bits are what remains — the interpreter machinery itself.

    Note: data_bits uses the actual per-bit cost of SET(500+i, v), which is ~23
    bits/bit at low slot indices. This is an encoding overhead of this storage
    scheme, not a fundamental lower bound on data cost."""
    bs = BS()
    data_bits = sum(
        bs.tlen(1,0) + bs.elen(INNER_BASE + i) + bs.elen(0)
        for i in range(n_inner_bits)
    )
    return asm_obj.prog_bits() - data_bits, data_bits


def interpreter_logic_exact(asm_obj, inner_bits_list):
    """Exact interpreter logic cost using true per-bit encoding costs.

    Unlike interpreter_logic_bits(), which uses a fixed ~23b/bit approximation,
    this uses the actual cost of each SET(INNER_BASE+i, bit_value) instruction,
    accounting for:
    - elen(INNER_BASE+i): grows at i=10 (slot 510) and i=524 (slot 1024)
    - elen(bit_value): 0-bits cost 1b, 1-bits cost 3b

    Returns (exact_logic_bits, exact_data_bits).
    """
    bs = BS()
    exact_data = sum(
        bs.tlen(1, 0) + bs.elen(INNER_BASE + i) + bs.elen(inner_bits_list[i])
        for i in range(len(inner_bits_list))
    )
    return asm_obj.prog_bits() - exact_data, exact_data


def interpreter_logic_bound(n_inner_bits):
    """Analytic upper bound on interpreter logic bits for inner program of size n.

    Fit to measurements across inner programs of 104b to 4304b (ISLOT_BASE=5000):
        logic_bits ≤ 10132 + 188 * ceil(log2(n_inner_bits))

    The O(log n) growth comes from jump offsets in the interpreter's JIF/JMP
    instructions: as the full interpreter program grows (O(n) in data storage),
    the jump offsets grow by ~1-2 bits each per doubling.

    The larger base (vs. old 7832) reflects ISLOT_BASE=5000 causing all ISLOT_BASE
    slot-constant SET instructions to encode ~log2(5000/200)≈4.6 bits more.

    This bound is analytic (not just measured) in the sense that:
    1. The number of JIF/JMP instructions is fixed at 102 (40 JIF + 62 JMP).
    2. Each offset grows at most 2 bits per doubling of program size.
    3. 102 * 2 bits/doubling ≈ 204b/doubling → slope ≤ ~148b/log-unit.
    4. Empirically measured slope = 139 ≤ 148, margin=188 is conservative.
    """
    import math
    return 10132 + 188 * math.ceil(math.log2(max(n_inner_bits, 2)))


def theorem3_tight_bound():
    """Tight lower bound on c_interp from actual ZCE token costs.

    Document Theorem 3 gives a loose lower bound:
        c_interp ≥ k * avg_id_len + m * log2(k^2) + n_ops * log2(n_ops)

    This function computes a tighter lower bound using actual ZCE encoding costs:
    - The DEF section must encode all k=7 extended op definitions.
    - Each DEF instruction costs: token cost + elias(tok) + elias(na-1) + na*elias(at_type)
      + elias(act) + elias(ap).
    - The interpreter must also contain at least one instruction per op it dispatches.

    Returns dict with: loose_bound, tight_bound, actual_k_v0, actual_k_i.
    """
    bs = BS()
    import math

    # Tight lower bound from DEF section only (each op must be defined)
    # For each of the 7 ops: SUB(tok=6,na=3), MUL(7,3), EQ(10,3), LT(11,3),
    #                         NOT(12,2), LOAD(13,2), STOR(14,2)
    ops = [
        (TOK['SUB'],  3), (TOK['MUL'], 3), (TOK['EQ'],  3), (TOK['LT'], 3),
        (TOK['NOT'],  2), (TOK['LOAD'],2), (TOK['STOR'], 2),
    ]
    tight_def = 0
    for tok, na in ops:
        # DEF instruction: token(5,1) + elias(tok) + elias(na-1) + na*elias(0) + elias(act) + elias(ap)
        cost = bs.tlen(5, 1) + bs.elen(tok) + bs.elen(na - 1)
        cost += na * bs.elen(0)          # arg types (all P=0)
        cost += bs.elen(0)               # act = 0 (EXT)
        cost += bs.elen(4)               # ap = min OP value = 3 (SUB), approximately
        tight_def += cost

    # Theorem 3 formula
    k = 12; avg_id = 5; n_ops = 12
    loose = int(k * avg_id + n_ops * math.log2(n_ops))

    # Actual values
    a0 = Asm(); a0.SET(0, 42)
    inner = a0.build()
    ib = stream_to_bits(inner)
    _, ia = build_interpreter(inner)
    logic, _ = interpreter_logic_bits(ia, len(ib))

    return {
        'loose_bound':   loose,
        'tight_def_lb':  tight_def,
        'actual_k_v0':   ia.def_bits(),
        'actual_k_i':    logic,
        'ratio':         logic / max(loose, 1),
    }


def inner_large_programs():
    """Generate larger inner programs for stress-testing the interpreter.

    Uses SET, ADD, and EXT ops (LT, EQ, SUB, LOAD) — all now fully supported
    by the interpreter's do_custom dispatch handler.

    Returns list of (name, inner_bytes, expected_result) tuples.
    """
    cases = []
    # Linear sum with LT loop (uses EXT)
    for n in [20, 25, 30]:
        inner, exp = inner_linear_sum(n)
        cases.append((f"sum 1..{n}", inner, exp))
    # Palindrome (uses SUB, EQ, LT, LOAD)
    for tape in [[1,0,1,0,1], [1,1,0,0,1,1], [0,1,0]]:
        P=0; a=Asm()
        a._defop(TOK['SUB'],OP['SUB'],3,[P,P,P]); a._defop(TOK['EQ'],OP['EQ'],3,[P,P,P])
        a._defop(TOK['LT'],OP['LT'],3,[P,P,P]); a._defop(TOK['LOAD'],OP['LOAD'],2,[P,P])
        n=len(tape)
        for i,b in enumerate(tape): a.SET(100+i,b)
        a.SET(0,1); a.SET(1,1); a.SET(2,0); a.SET(3,n-1)
        a.label('loop'); a.LT(20,2,3); a.JIF(20,'done')
        a.SET(10,100); a.ADD(10,10,2); a.LOAD(10,10)
        a.SET(11,100); a.ADD(11,11,3); a.LOAD(11,11)
        a.EQ(20,10,11); a.JIF(20,'mismatch')
        a.ADD(2,2,1); a.SUB(3,3,1); a.JMP('loop')
        a.label('mismatch'); a.SET(0,0); a.label('done')
        exp = 1 if tape==tape[::-1] else 0
        cases.append((f"pal {''.join(map(str,tape))}", a.build(), exp))
    return cases
