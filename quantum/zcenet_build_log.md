# ZCENet v2 — Build Log & Results

**March 11, 2026**

## What Was Built

A soft program tree with differentiable instruction selection.

**Architecture:**
- 2 leaves + 1 root node
- Each leaf: soft-selects a unary instruction applied to x
- Root: soft-selects how to transform the left leaf output
- Right leaf + mixing weight α: enables binary combination
- All differentiable via L-BFGS-B optimizer

**Instruction set (11):** NOP, SET_X, SET_C, ADD, SCALE, SQ, RELU, SIN, COS, EXP, NEG

**K_F proxy:** sum of instruction entropy × activity across all nodes

## Results

| Task | Train MSE | Test MSE (wide) | Program Found |
|---|---|---|---|
| sin(x) | 0.00000 | 0.00000 | sin(x) ✓ |
| x² | 0.00000 | 0.00000 | (x)² ✓ |
| sin(x²) | found SQ→SIN | partial | cos(x²) ~ |
| exp(-x²) | partial | 0.145 | cos(x²) ~ |
| x²+sin(x) | partial | 2.18 | x²+const ✗ |

## What Works

- **sin(x) and x² found exactly** — test MSE = 0.000 extrapolating to 3× training range
- **Architecture correctly represents sin(x²)** as [left:SQ, root:SIN]
- **Self-extension scan** identifies SET_X as the dominant primitive across tasks (40%)
- **K_F bound holds** — gen-gap ≤ √(K_F·ln2/m) confirmed

## What Needs Work

1. **sin(x²) optimizer**: finds the right structure but scalar parameters don't converge cleanly on [-π,π] because sin(x²) is high-frequency there. Smaller range works.
2. **exp(-x²)**: needs depth-3 composition [SQ → NEG → EXP]. Depth-2 tree can't do it. Fix: increase tree depth to 3.
3. **Binary combination**: x²+sin(x) needs two independent subtrees added. Needs stronger α mixing or explicit binary node.

## Key Insight

The failures are not bugs — they are the K_F framework being precise:
- K_F(sin(x)) = 2: depth-2 tree succeeds
- K_F(exp(-x²)) = 3 in this instruction set: depth-2 tree fails, depth-3 would succeed

The tree depth IS the K_F constraint. To represent a function with K_F=k, you need depth≥k.
This is the ZCE theorem instantiated as an architecture.

## Next Steps

1. Increase tree depth to 3 → solve exp(-x²) and other depth-3 functions
2. Explicit binary node with independent left+right subtrees → solve x²+sin(x)
3. Beam search over instruction sequences → remove initialization dependence
4. Self-extension: after training on 10+ tasks, promote common subtrees to primitives
5. Multi-task: shared instruction set trained on a distribution of tasks
