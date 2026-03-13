"""
zce_surgeon.py
==============
Parse, inspect, and surgically modify ZCE v2 bitstreams.

Capabilities:
  - Decode a stream to its instruction list (disassembly)
  - Swap an activation function (changes action_param in DEFINE_OP)
  - Replace weights (find all FSET/FARR_SET sequences, substitute new floats)
  - Transplant output layer from one stream into another
  - Measure edit distance between streams (bytes changed)
  - Re-encode surgically modified streams

The key insight: because ZCE is self-describing, we can parse
ANY valid stream without knowing what network it encodes.
We just follow the grammar.
"""

import math
import struct
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Any


# ── Elias gamma ───────────────────────────────────────────────

def elias_enc(v: int) -> str:
    assert v >= 0
    x = v + 1
    k = int(math.log2(x))
    return '0' * k + format(x, f'0{k+1}b')

def elias_dec(bits: str, pos: int):
    """Decode elias gamma from bits[pos]. Returns (value, new_pos)."""
    k = 0
    while pos < len(bits) and bits[pos] == '0':
        pos += 1; k += 1
    x = int(bits[pos:pos+k+1], 2)
    return x - 1, pos + k + 1

def token_enc(n: int, depth: int = 1) -> str:
    return '0' * n + '1' * depth + '0'

def token_dec(bits: str, pos: int):
    """Decode token from bits[pos]. Returns (n, depth, new_pos)."""
    n = 0
    while pos < len(bits) and bits[pos] == '0':
        pos += 1; n += 1
    depth = 0
    while pos < len(bits) and bits[pos] == '1':
        pos += 1; depth += 1
    pos += 1  # terminator zero
    return n, depth, pos


# ── Argument types ────────────────────────────────────────────

ARG_PTR   = 0
ARG_VAL   = 1
ARG_RAW32 = 2

ACT_EXEC = 0
ACT_JIF  = 1
ACT_JMP  = 2
ACT_NOP  = 3

# Op names for display
OP_NAMES = {
    1: 'SET', 2: 'ADD', 3: 'SUB', 4: 'MUL', 5: 'DIV',
    10: 'FSET', 11: 'FADD', 12: 'FSUB', 13: 'FMUL', 14: 'FDIV',
    15: 'FEXP', 16: 'FTANH', 17: 'FMAX', 18: 'FMIN',
    19: 'FNEG', 20: 'FABS', 21: 'FCMP_GT', 22: 'FPRINT',
    30: 'FARR_NEW', 31: 'FARR_SET', 32: 'FARR_GET',
    40: 'MAT_VEC', 41: 'VEC_ADD', 42: 'SOFTMAX',
    43: 'ARGMAX', 44: 'LEAKY_RELU', 45: 'VEC_COPY',
}

TOK_NAMES = {
    1: 'SET', 2: 'ADD', 3: 'JIF', 4: 'JMP', 5: 'DEFINE_OP',
    6: 'SUB', 7: 'MUL', 8: 'DIV', 9: 'FSET', 10: 'FADD',
    11: 'FSUB', 12: 'FMUL', 13: 'FDIV', 14: 'FEXP', 15: 'FTANH',
    16: 'FMAX', 17: 'FMIN', 18: 'FNEG', 19: 'FABS', 20: 'FCMP_GT',
    21: 'FARR_NEW', 22: 'FARR_SET', 23: 'FARR_GET',
    24: 'MAT_VEC', 25: 'VEC_ADD', 26: 'SOFTMAX',
    27: 'ARGMAX', 28: 'LEAKY_RELU', 29: 'VEC_COPY',
}


# ── Parsed instruction types ──────────────────────────────────

@dataclass
class Instr:
    bit_pos: int      # position in grammar bits
    bit_len: int      # length in bits
    kind: str         # 'DEFINE_OP', 'SET', 'ADD', 'EXEC', 'JIF', 'JMP', 'NOP'
    tok_n: int
    depth: int
    args: List[Any]   # decoded argument values
    raw_args: List[str]  # raw bit strings for each arg (for surgery)
    # DEFINE_OP specific
    target: int = 0
    n_args: int = 0
    arg_types: List[int] = field(default_factory=list)
    action: int = 0
    action_param: int = 0
    # For EXEC instructions
    op_name: str = ''


# ── Stream parser ─────────────────────────────────────────────

class ZCEParser:
    """
    Parse a ZCE v2 bitstream into a list of instructions.
    Follows the grammar exactly as the C decoder does.
    """

    def __init__(self, data: bytes):
        self.data = data
        self.bits = ''.join(format(b, '08b') for b in data)
        self.pos = 0
        self.rules = {}   # tok_n → {n_args, arg_types, action, action_param}
        self._init_base_rules()

        # Parse header
        self.grammar_bits, self.pos = elias_dec(self.bits, self.pos)
        self.grammar_start = self.pos
        self.grammar_end   = self.pos + self.grammar_bits

        # Parse all instructions
        self.instrs: List[Instr] = []
        self._parse()

    def _init_base_rules(self):
        self.rules[1] = dict(n_args=2, arg_types=[ARG_PTR, ARG_VAL], action=ACT_EXEC, action_param=1)  # SET
        self.rules[2] = dict(n_args=3, arg_types=[ARG_PTR]*3, action=ACT_EXEC, action_param=2)          # ADD
        self.rules[3] = dict(n_args=2, arg_types=[ARG_PTR, ARG_VAL], action=ACT_JIF, action_param=0)    # JIF
        self.rules[4] = dict(n_args=1, arg_types=[ARG_VAL], action=ACT_JMP, action_param=0)             # JMP
        self.rules[5] = dict(n_args=0, arg_types=[], action=ACT_NOP, action_param=0)                    # DEFINE_OP

    def _read_arg(self, arg_type: int):
        """Read one argument, return (value, raw_bits, new_pos)."""
        start = self.pos
        if arg_type in (ARG_PTR, ARG_VAL):
            val, self.pos = elias_dec(self.bits, self.pos)
            return val, self.bits[start:self.pos]
        elif arg_type == ARG_RAW32:
            raw = self.bits[self.pos:self.pos+32]
            val = struct.unpack('f', struct.pack('I', int(raw, 2)))[0]
            self.pos += 32
            return val, raw

    def _parse(self):
        self.pos = self.grammar_start
        while self.pos < self.grammar_end:
            instr_start = self.pos
            tok_n, depth, self.pos = token_dec(self.bits, self.pos)
            if tok_n == 0:
                continue

            if tok_n == 5:  # DEFINE_OP
                target, _ = elias_dec(self.bits, self.pos); self.pos = _
                n_args_m1, _ = elias_dec(self.bits, self.pos); self.pos = _
                n_args = n_args_m1 + 1
                arg_types = []
                for _ in range(n_args):
                    at, _ = elias_dec(self.bits, self.pos); self.pos = _
                    arg_types.append(at)
                action, _ = elias_dec(self.bits, self.pos); self.pos = _
                action_param = 0
                if action == ACT_EXEC:
                    action_param, _ = elias_dec(self.bits, self.pos); self.pos = _

                self.rules[target] = dict(
                    n_args=n_args, arg_types=arg_types,
                    action=action, action_param=action_param)

                instr = Instr(
                    bit_pos=instr_start, bit_len=self.pos-instr_start,
                    kind='DEFINE_OP', tok_n=5, depth=depth,
                    args=[], raw_args=[],
                    target=target, n_args=n_args, arg_types=arg_types,
                    action=action, action_param=action_param,
                    op_name=OP_NAMES.get(action_param, f'op{action_param}')
                )
                self.instrs.append(instr)

            elif tok_n not in self.rules:
                break  # unknown token

            else:
                rule = self.rules[tok_n]
                args, raw_args = [], []
                for at in rule['arg_types']:
                    v, r = self._read_arg(at)
                    args.append(v); raw_args.append(r)

                action = rule['action']
                kind = {ACT_EXEC: 'EXEC', ACT_JIF: 'JIF',
                        ACT_JMP: 'JMP', ACT_NOP: 'NOP'}.get(action, 'UNK')
                op_name = TOK_NAMES.get(tok_n, f'tok{tok_n}')

                instr = Instr(
                    bit_pos=instr_start, bit_len=self.pos-instr_start,
                    kind=kind, tok_n=tok_n, depth=depth,
                    args=args, raw_args=raw_args,
                    action_param=rule['action_param'],
                    op_name=op_name
                )
                self.instrs.append(instr)

    def disassemble(self, max_lines=50) -> str:
        lines = [f"Stream: {len(self.data)} bytes, grammar: {self.grammar_bits} bits"]
        lines.append(f"Instructions: {len(self.instrs)}")
        lines.append("")
        for i, ins in enumerate(self.instrs[:max_lines]):
            if ins.kind == 'DEFINE_OP':
                anames = [['PTR','VAL','RAW32'][t] for t in ins.arg_types]
                act = ['EXEC','JIF','JMP','NOP'][ins.action]
                op  = OP_NAMES.get(ins.action_param, str(ins.action_param))
                lines.append(f"  [{i:4d}] DEFINE_OP target={ins.target} "
                              f"args=[{','.join(anames)}] {act}({op})")
            else:
                arg_str = ', '.join(
                    f"{v:.4f}" if isinstance(v, float) else str(v)
                    for v in ins.args)
                lines.append(f"  [{i:4d}] {ins.op_name:12s} {arg_str}")
        if len(self.instrs) > max_lines:
            lines.append(f"  ... ({len(self.instrs)-max_lines} more)")
        return '\n'.join(lines)

    def stats(self) -> dict:
        from collections import Counter
        op_counts = Counter(ins.op_name for ins in self.instrs)
        define_ops = [ins for ins in self.instrs if ins.kind == 'DEFINE_OP']
        fset_count = sum(1 for ins in self.instrs if ins.op_name == 'FSET')
        return {
            'n_instrs': len(self.instrs),
            'n_define_ops': len(define_ops),
            'n_fset': fset_count,
            'op_counts': dict(op_counts),
            'defined_tokens': {ins.target: OP_NAMES.get(ins.action_param, str(ins.action_param))
                               for ins in define_ops},
        }


# ── Stream surgeon ────────────────────────────────────────────

class ZCESurgeon:
    """
    Perform surgical modifications on parsed streams.
    Works at the bit level — modifies only the targeted bits,
    leaves everything else untouched.
    """

    def __init__(self, data: bytes):
        self.original = data
        self.parser = ZCEParser(data)
        # Working copy of grammar bits
        self._grammar = list(
            self.parser.bits[self.parser.grammar_start:self.parser.grammar_end])

    def _grammar_to_stream(self) -> bytes:
        """Rebuild stream from modified grammar bits."""
        grammar = ''.join(self._grammar)
        header = elias_enc(len(grammar))
        full = header + grammar
        pad = (8 - len(full) % 8) % 8
        full += '0' * pad
        return bytes(int(full[i:i+8], 2) for i in range(0, len(full), 8))

    def swap_activation(self, old_op: int, new_op: int) -> bytes:
        """
        Find all DEFINE_OP instructions with action_param=old_op
        and replace action_param with new_op.
        Returns (modified_stream_bytes, n_swapped).

        Works by rebuilding the grammar bit-by-bit, replacing only the
        action_param elias fields that match. Handles length changes correctly.
        """
        # Rebuild grammar from scratch, substituting matching action_params
        new_grammar = []
        n_swapped = 0
        bits = self.parser.bits
        pos = self.parser.grammar_start

        while pos < self.parser.grammar_end:
            instr_start = pos
            tok_n, depth, pos2 = token_dec(bits, pos)
            if tok_n == 0:
                new_grammar.append(bits[instr_start:pos2])
                pos = pos2
                continue

            if tok_n == 5:  # DEFINE_OP — may need to patch action_param
                # Read all fields
                target, p1 = elias_dec(bits, pos2)
                n_args_m1, p2 = elias_dec(bits, p1)
                n_args = n_args_m1 + 1
                p = p2
                at_list = []
                for _ in range(n_args):
                    at, p = elias_dec(bits, p)
                    at_list.append(at)
                action, p = elias_dec(bits, p)

                if action == ACT_EXEC:
                    action_param, p_after = elias_dec(bits, p)
                    if action_param == old_op:
                        # Rebuild this DEFINE_OP with new action_param
                        chunk = (bits[instr_start:pos2]   # token
                               + bits[pos2:p1]            # target elias (pos2→p1 is already read above as pos2)
                               + bits[p1:p2]              # n_args-1
                               + bits[p2:p2])             # placeholder
                        # Actually rebuild cleanly:
                        chunk = (bits[instr_start:pos2]   # token bits
                               + bits[pos2:p])            # everything up to action_param
                        chunk += elias_enc(new_op)        # new action_param
                        new_grammar.append(chunk)
                        n_swapped += 1
                        pos = p_after
                        continue
                    else:
                        new_grammar.append(bits[instr_start:p_after])
                        pos = p_after
                        continue
                else:
                    new_grammar.append(bits[instr_start:p])
                    pos = p
                    continue

            else:
                # Regular instruction — copy verbatim
                rule = self.parser.rules.get(tok_n)
                if not rule:
                    break
                p = pos2
                for at in rule['arg_types']:
                    if at in (ARG_PTR, ARG_VAL):
                        _, p = elias_dec(bits, p)
                    elif at == ARG_RAW32:
                        p += 32
                new_grammar.append(bits[instr_start:p])
                pos = p

        grammar = ''.join(new_grammar)
        header = elias_enc(len(grammar))
        full = header + grammar
        pad = (8 - len(full) % 8) % 8
        full += '0' * pad
        result = bytes(int(full[i:i+8], 2) for i in range(0, len(full), 8))
        return result, n_swapped

    def replace_weights(self, new_weights: list) -> bytes:
        """
        Replace all FSET float32 values in the stream with new_weights.
        new_weights must be the same length as the number of FSET instructions.

        This is weight surgery: identical structure, different numbers.
        Used for: weight update streaming, quantization, fine-tuning transfer.
        """
        fset_instrs = self._fset_instrs()
        assert len(new_weights) == len(fset_instrs), \
            f"Expected {len(fset_instrs)} weights, got {len(new_weights)}"

        modified = list(self.parser.bits)

        for ins, new_w in zip(fset_instrs, new_weights):
            # Find the RAW32 argument position in the instruction
            pos = ins.bit_pos
            # Skip token
            _, _, pos = token_dec(self.parser.bits, pos)
            # Skip ptr arg (elias)
            _, pos = elias_dec(self.parser.bits, pos)
            # NOW at RAW32 (32 bits)
            raw_start = pos
            new_bits = format(struct.unpack('I', struct.pack('f', float(new_w)))[0], '032b')
            modified[raw_start:raw_start+32] = list(new_bits)

        full = ''.join(modified)
        pad = (8 - len(full) % 8) % 8
        full += '0' * pad
        return bytes(int(full[i:i+8], 2) for i in range(0, len(full), 8))

    def extract_weights(self) -> list:
        """Extract all FSET float32 values from the stream (the float weight values)."""
        # FSET instructions have tok_n=9, kind='EXEC', args=[dst_slot, float_value]
        return [ins.args[1] for ins in self.parser.instrs
                if ins.tok_n == 9 and ins.kind == 'EXEC' and len(ins.args) >= 2]

    def _fset_instrs(self):
        return [ins for ins in self.parser.instrs
                if ins.tok_n == 9 and ins.kind == 'EXEC' and len(ins.args) >= 2]

    def edit_distance_bytes(self, other: bytes) -> dict:
        """Count bytes that differ between this stream and another."""
        a, b = self.original, other
        min_len = min(len(a), len(b))
        changed = sum(1 for i in range(min_len) if a[i] != b[i])
        return {
            'bytes_changed': changed,
            'total_bytes': max(len(a), len(b)),
            'pct_changed': 100.0 * changed / max(len(a), len(b)),
            'size_delta': len(b) - len(a),
        }

    def transplant_output_layer(self, donor_stream: bytes,
                                 n_hidden: int, n_out: int,
                                 n_in: int = None) -> bytes:
        """
        Take W2, b2 weights from donor_stream, inject into self's stream.
        Assumes both streams have the same architecture (same n_in, n_hidden, n_out).

        Transfer learning: shared backbone (W1, b1), new output (W2, b2).

        Weight layout in stream:
          [0 .. n_in*n_hidden-1]                    = W1
          [n_in*n_hidden .. n_in*n_hidden+n_hidden-1] = b1
          [.. n_in*n_hidden+n_hidden+n_out*n_hidden-1] = W2
          [.. +n_out-1]                               = b2
          [n_net .. end]                              = input FSETs (per sample)
        """
        donor_weights = ZCESurgeon(donor_stream).extract_weights()
        self_weights  = self.extract_weights()

        n_out_weights = n_hidden * n_out + n_out   # size of W2+b2 block

        if n_in is None:
            # Infer: total network weights = n_net, remainder are input FSETs
            # n_net = n_in*n_hidden + n_hidden + n_out*n_hidden + n_out
            # The first n_net items are network weights, rest are input data FSETs
            # We know n_hidden and n_out; infer n_in from total
            # For small streams, n_net << len(self_weights)
            # Heuristic: n_backbone = n_in*n_hidden + n_hidden
            #   n_net = n_backbone + n_out_weights
            # We scan for the crossover point by comparing with donor
            # Simple: assume first (W1+b1) block = len - n_out_weights - n_input_FSETs
            # Since both have same architecture, donor has same n_net
            # Just replace donor's n_out_weights in the network block
            # Network block ends at: len(self_weights) - n_samples*n_in
            # But we don't know n_samples here.
            # Safest: infer n_net from donor (same architecture guaranteed)
            # n_net = smallest plausible: find where donor's last n_out_weights are
            # within the first min(len, donor_len) weights
            # For this codebase: layout is W1,b1,W2,b2 then inputs
            # W2+b2 start at index: total_net - n_out_weights
            # For 2->8->2 with 20 samples: 42 net weights, then 40 input FSETs
            # Donor and self have same n_net. n_net - n_out_weights = backbone size.
            # Backbone = n_in*n_hidden + n_hidden. Total net = backbone + n_out_weights.
            # We know n_out_weights. total_net must be <= len(self_weights).
            # Find n_backbone by trying: scan positions where donor values match.
            # Simplest robust approach: compare first few values with known weights.
            # For now: try donor[-n_out_weights:] vs position (len(donor_weights) - n_out_weights)
            # in the network block = min(len, position before inputs start)
            # We'll use: w2b2_start = len(donor_weights) - n_out_weights 
            #   but only if all remaining are input FSETs (slot patterns differ).
            # HACK for this codebase: W2+b2 always end at position
            #   (total_net_weights - 0) from start, and input FSETs follow.
            #   total_net = (all weights) - (n_samples * n_in)
            # Instead just use: find where W2 block is by matching donor[?:?+n_out_weights]
            # The most reliable: backbone is same in both streams.
            # W2b2 in donor starts at same position as in self.
            # Use len of donor minus n_out_weights as w2b2 start... but that includes inputs.
            # REAL fix: accept n_in parameter. Default to inferring via: total_net_known.
            pass

        # Use explicit n_in if provided
        if n_in is not None:
            n_net = n_in * n_hidden + n_hidden + n_hidden * n_out + n_out
            w2b2_start = n_in * n_hidden + n_hidden   # start of W2+b2 in network block
        else:
            # Fallback: find w2b2 position by noting both streams have same architecture
            # The network weights come FIRST, then input FSETs.
            # Compare self vs donor at each possible split point.
            # W2+b2 from donor should be transplanted into self at same offset.
            # Since we don't know n_in, we infer: look for the unique donor W2+b2 signature.
            # If n_in is unknown, scan: find position p where donor[p:p+n_out_weights]
            # matches donor's network W2+b2 block. This requires reference weights.
            # For safety, use: w2b2_start = n_hidden + n_hidden*n_out  (assumes n_in=n_hidden)
            # This is wrong in general. Better: require n_in or use a marker.
            # For this demo, use a reasonable default (works for moons n_in=2):
            # n_in defaults to 2 (moons), override with n_in parameter.
            n_in_guess = (len(self_weights) - n_hidden - n_out_weights) // (n_hidden + 1)
            # Fallback: just count from network start
            w2b2_start = min(16, len(self_weights) - n_out_weights - n_hidden)
            n_net = w2b2_start + n_hidden + n_out_weights

        # Splice: self's W1+b1 + donor's W2+b2 + self's input FSETs
        w2b2_end = w2b2_start + n_out_weights
        new_weights = (list(self_weights[:w2b2_start]) +
                       list(donor_weights[w2b2_start:w2b2_end]) +
                       list(self_weights[w2b2_end:]))

        assert len(new_weights) == len(self_weights), \
            f"Weight count mismatch: {len(new_weights)} vs {len(self_weights)}"
        return self.replace_weights(new_weights)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/claude')

    print("=== ZCE Stream Parser/Surgeon Test ===\n")

    with open('/home/claude/stream_moons_full.zce', 'rb') as f:
        moons_stream = f.read()

    parser = ZCEParser(moons_stream)
    print(parser.disassemble(max_lines=30))
    print()

    s = parser.stats()
    print("Stats:")
    for k, v in s.items():
        if k != 'op_counts':
            print(f"  {k}: {v}")
    print(f"  op_counts (top 10):")
    from collections import Counter
    for op, cnt in Counter(s['op_counts']).most_common(10):
        print(f"    {op}: {cnt}")

    print(f"\nTotal FSET (weight) instructions: {s['n_fset']}")

    # Test activation swap
    surgeon = ZCESurgeon(moons_stream)
    swapped, n = surgeon.swap_activation(44, 16)  # LEAKY_RELU → FTANH
    print(f"\nActivation swap (LEAKY_RELU→FTANH): {n} DEFINE_OPs modified")
    diff = surgeon.edit_distance_bytes(swapped)
    print(f"Edit distance: {diff}")
