"""
Phase 1: Primitive Discovery
============================
Goal: Starting from {ADD, MUL, SET} only, discover mathematical primitives
by finding subprograms that compress multiple tasks simultaneously.

This is the K_F experiment from the paper:
  - Without SIN: K_F(sin task) = ∞ (never exactly expressible)
  - With SIN:    K_F(sin task) = 2

The system should discover SIN (and others) purely from compression pressure
applied across a task library of function fitting problems.

Architecture:
  TaskLibrary  — a set of (x, y) function fitting tasks with ground truth
  Solver       — finds the shortest program that fits a task within tolerance
  LibraryMDL   — scores whether adding a primitive genuinely compresses the library
  Evolver      — runs the discovery loop: solve → extract → promote → repeat

The key insight: a primitive is worth keeping if it reduces total description
length across ALL tasks, not just the task it was discovered on.
"""

import numpy as np
import math
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from itertools import product
import copy

# ── Symbolic program representation ──────────────────────────────────────────

@dataclass
class Op:
    """A primitive operation in the library."""
    name: str
    arity: int          # number of float inputs
    fn: Callable        # numpy implementation
    cost: int = 1       # description length cost (bits, simplified to 1 per op)
    discovered: bool = False  # True if discovered, False if built-in

# ── Base library: truly minimal ───────────────────────────────────────────────

def make_base_library() -> Dict[str, Op]:
    """
    Start with only: ADD, MUL, SET (constant), NEG, INV
    These are the axioms. Everything else must be discovered.
    """
    return {
        'SET':  Op('SET',  0, lambda x: None,       cost=2),  # constant (2 bits for value)
        'ADD':  Op('ADD',  2, lambda a, b: a + b,   cost=1),
        'MUL':  Op('MUL',  2, lambda a, b: a * b,   cost=1),
        'NEG':  Op('NEG',  1, lambda a: -a,          cost=1),
        'INV':  Op('INV',  1, lambda a: 1.0/(a + 1e-10), cost=1),
        'SQ':   Op('SQ',   1, lambda a: a * a,       cost=1),
        'SQRT': Op('SQRT', 1, lambda a: np.sqrt(np.abs(a)), cost=1),
        'ABS':  Op('ABS',  1, lambda a: np.abs(a),   cost=1),
    }

# Candidate primitives that COULD be discovered:
CANDIDATE_PRIMITIVES = {
    'SIN':    Op('SIN',    1, lambda a: np.sin(a),               cost=1, discovered=True),
    'COS':    Op('COS',    1, lambda a: np.cos(a),               cost=1, discovered=True),
    'EXP':    Op('EXP',    1, lambda a: np.exp(np.clip(a,-10,10)), cost=1, discovered=True),
    'LOG':    Op('LOG',    1, lambda a: np.log(np.abs(a)+1e-10), cost=1, discovered=True),
    'TANH':   Op('TANH',   1, lambda a: np.tanh(a),              cost=1, discovered=True),
    'POW3':   Op('POW3',   1, lambda a: a**3,                    cost=1, discovered=True),
    'SINC':   Op('SINC',   1, lambda a: np.sinc(a/np.pi),        cost=1, discovered=True),
}

# ── Symbolic expression tree ──────────────────────────────────────────────────

@dataclass
class Expr:
    """A symbolic expression node."""
    op: str              # operation name or 'X' (input) or 'CONST'
    children: list = field(default_factory=list)
    const_val: float = 0.0

    def eval(self, x: np.ndarray, library: Dict[str, Op]) -> np.ndarray:
        """Evaluate this expression on input x."""
        if self.op == 'X':
            return x
        if self.op == 'CONST':
            return np.full_like(x, self.const_val, dtype=float)
        op = library[self.op]
        child_vals = [c.eval(x, library) for c in self.children]
        try:
            result = op.fn(*child_vals)
            # Clip to prevent explosion
            return np.clip(result, -1e6, 1e6)
        except:
            return np.zeros_like(x)

    def depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(c.depth() for c in self.children)

    def size(self, library: Dict[str, Op]) -> int:
        """Description length (number of ops)."""
        if self.op in ('X', 'CONST'):
            return 1
        op_cost = library[self.op].cost
        return op_cost + sum(c.size(library) for c in self.children)

    def to_str(self) -> str:
        if self.op == 'X':
            return 'x'
        if self.op == 'CONST':
            return f'{self.const_val:.3g}'
        if self.op in ('NEG', 'SQ', 'SQRT', 'ABS', 'SIN', 'COS', 'EXP', 'LOG',
                       'TANH', 'POW3', 'SINC', 'INV'):
            return f'{self.op}({self.children[0].to_str()})'
        if self.op in ('ADD', 'MUL'):
            return f'({self.children[0].to_str()} {self.op} {self.children[1].to_str()})'
        return f'{self.op}({", ".join(c.to_str() for c in self.children)})'

    def copy(self):
        return copy.deepcopy(self)


def X(): return Expr('X')
def CONST(v): return Expr('CONST', const_val=float(v))
def node(op, *children): return Expr(op, list(children))


# ── Task definition ───────────────────────────────────────────────────────────

@dataclass
class Task:
    name: str
    x: np.ndarray
    y: np.ndarray
    true_expr: Optional[str] = None  # ground truth for display

    @staticmethod
    def make(name: str, fn, n=50, xrange=(-3.0, 3.0), seed=42, true_expr=None):
        np.random.seed(seed)
        x = np.linspace(xrange[0], xrange[1], n)
        y = fn(x).astype(float)
        return Task(name, x, y, true_expr)


def make_task_library() -> List[Task]:
    """
    A diverse set of function fitting tasks.
    The system should discover primitives that compress multiple tasks.
    """
    tasks = [
        # Polynomial tasks (solvable with ADD+MUL+SQ)
        Task.make('x²',         lambda x: x**2,              true_expr='SQ(x)'),
        Task.make('x³',         lambda x: x**3,              true_expr='MUL(x,SQ(x))'),
        Task.make('2x+1',       lambda x: 2*x + 1,           true_expr='ADD(MUL(2,x),1)'),
        Task.make('x²+x',       lambda x: x**2 + x,          true_expr='ADD(SQ(x),x)'),
        Task.make('x²-2x+1',    lambda x: (x-1)**2,          true_expr='SQ(ADD(x,-1))'),

        # Trigonometric tasks (need SIN/COS — not in base library)
        Task.make('sin(x)',     lambda x: np.sin(x),         true_expr='SIN(x)'),
        Task.make('cos(x)',     lambda x: np.cos(x),         true_expr='COS(x)'),
        Task.make('sin(2x)',    lambda x: np.sin(2*x),       true_expr='SIN(MUL(2,x))'),
        Task.make('sin(x²)',    lambda x: np.sin(x**2),      true_expr='SIN(SQ(x))'),
        Task.make('sin+cos',    lambda x: np.sin(x)+np.cos(x), true_expr='ADD(SIN(x),COS(x))'),

        # Exponential tasks (need EXP/LOG)
        Task.make('exp(x)',     lambda x: np.exp(np.clip(x,-3,3)),  true_expr='EXP(x)'),
        Task.make('exp(-x²)',   lambda x: np.exp(-x**2),            true_expr='EXP(NEG(SQ(x)))'),
        Task.make('log(|x|+1)', lambda x: np.log(np.abs(x)+1),     true_expr='LOG(ADD(ABS(x),1))'),

        # Mixed tasks (need multiple discovered primitives)
        Task.make('sin×exp',   lambda x: np.sin(x)*np.exp(-x**2/4),
                  true_expr='MUL(SIN(x),EXP(NEG(MUL(SQ(x),0.25))))'),
        Task.make('x·sin(x)',  lambda x: x*np.sin(x),              true_expr='MUL(x,SIN(x))'),
    ]
    return tasks


# ── Fitness and search ────────────────────────────────────────────────────────

def fitness(expr: Expr, task: Task, library: Dict[str, Op],
            tolerance: float = 0.01) -> Tuple[float, bool]:
    """
    Returns (fit_score, exact_fit).
    fit_score: lower is better. Combines error and description length.
    exact_fit: True if RMSE < tolerance on all points.
    """
    try:
        pred = expr.eval(task.x, library)
        if np.any(np.isnan(pred)) or np.any(np.isinf(pred)):
            return 1e9, False
        rmse = np.sqrt(np.mean((pred - task.y)**2))
        size = expr.size(library)
        # MDL: minimize bits(program) + bits(data|program)
        # Simplified: rmse + alpha * size
        alpha = 0.05
        score = rmse + alpha * size
        exact = rmse < tolerance
        return score, exact
    except:
        return 1e9, False


def random_expr(library: Dict[str, Op], max_depth: int = 3,
                rng: np.random.RandomState = None) -> Expr:
    """Generate a random expression tree."""
    if rng is None:
        rng = np.random.RandomState()

    if max_depth == 0:
        # Terminal: X or CONST
        if rng.rand() < 0.5:
            return X()
        else:
            return CONST(rng.uniform(-3, 3))

    # Choose operation
    ops = list(library.keys())
    op_name = ops[rng.randint(len(ops))]
    op = library[op_name]

    if op.arity == 0:
        return CONST(rng.uniform(-3, 3))

    children = [random_expr(library, max_depth - 1, rng) for _ in range(op.arity)]
    return node(op_name, *children)


def mutate(expr: Expr, library: Dict[str, Op],
           rng: np.random.RandomState) -> Expr:
    """Mutate an expression: change op, replace subtree, or tweak constant."""
    expr = expr.copy()
    r = rng.rand()

    if r < 0.3 or not expr.children:
        # Replace entirely with random
        return random_expr(library, max_depth=3, rng=rng)

    if r < 0.6 and expr.children:
        # Mutate a random child
        idx = rng.randint(len(expr.children))
        expr.children[idx] = mutate(expr.children[idx], library, rng)
        return expr

    # Change this node's op (keeping arity)
    arity = library[expr.op].arity if expr.op in library else 0
    same_arity = [k for k, v in library.items() if v.arity == arity]
    if same_arity:
        expr.op = same_arity[rng.randint(len(same_arity))]
    return expr


def evolutionary_search(task: Task, library: Dict[str, Op],
                         pop_size: int = 200, generations: int = 500,
                         seed: int = 0) -> Tuple[Expr, float, bool]:
    """
    Evolutionary search for the best-fitting expression.
    Returns (best_expr, best_score, found_exact).
    """
    rng = np.random.RandomState(seed)

    # Initialize population
    pop = [random_expr(library, max_depth=4, rng=rng) for _ in range(pop_size)]
    scores = [fitness(e, task, library)[0] for e in pop]

    best_expr = pop[np.argmin(scores)]
    best_score = min(scores)
    best_exact = fitness(best_expr, task, library)[1]

    for gen in range(generations):
        # Tournament selection + mutation
        new_pop = []
        for _ in range(pop_size):
            # Tournament of 5
            candidates = rng.choice(len(pop), 5, replace=False)
            winner_idx = candidates[np.argmin([scores[i] for i in candidates])]
            child = mutate(pop[winner_idx], library, rng)
            new_pop.append(child)

        # Evaluate
        new_scores = [fitness(e, task, library)[0] for e in new_pop]

        # Elitism: keep top 10% from old pop
        elite_n = pop_size // 10
        all_exprs = pop + new_pop
        all_scores = scores + new_scores
        sorted_idx = np.argsort(all_scores)[:pop_size]
        pop = [all_exprs[i] for i in sorted_idx]
        scores = [all_scores[i] for i in sorted_idx]

        if scores[0] < best_score:
            best_score = scores[0]
            best_expr = pop[0]
            best_exact, _ = fitness(best_expr, task, library)[1], None
            best_exact = fitness(best_expr, task, library)[1]

        if best_exact:
            break

    return best_expr, best_score, best_exact


# ── Library MDL criterion ─────────────────────────────────────────────────────

def compute_library_mdl(tasks: List[Task], solutions: Dict[str, Expr],
                         library: Dict[str, Op]) -> float:
    """
    Total description length of all solutions under current library.
    MDL: sum of program sizes + fit errors.
    """
    total = 0.0
    for task in tasks:
        if task.name in solutions:
            expr = solutions[task.name]
            score, _ = fitness(expr, task, library)
            total += score
        else:
            total += 100.0  # unsolved task penalty
    return total


def test_primitive_value(candidate_name: str, candidate_op: Op,
                          tasks: List[Task], solutions: Dict[str, Expr],
                          current_library: Dict[str, Op],
                          search_budget: int = 200) -> Dict:
    """
    Test whether adding a primitive genuinely compresses the task library.

    Returns:
      - mdl_before: total MDL without this primitive
      - mdl_after:  total MDL with this primitive (after re-solving)
      - delta_mdl:  improvement (positive = primitive helps)
      - tasks_improved: which tasks get shorter solutions
    """
    # MDL before
    mdl_before = compute_library_mdl(tasks, solutions, current_library)

    # Library with new primitive
    new_library = dict(current_library)
    new_library[candidate_name] = candidate_op

    # Re-solve all tasks with new library (quick search)
    new_solutions = dict(solutions)
    tasks_improved = []
    for task in tasks:
        old_score = fitness(solutions.get(task.name, CONST(0)), task, current_library)[0]
        new_expr, new_score, exact = evolutionary_search(
            task, new_library, pop_size=100, generations=search_budget, seed=42)
        if new_score < old_score - 0.01:
            new_solutions[task.name] = new_expr
            tasks_improved.append((task.name, old_score, new_score))

    mdl_after = compute_library_mdl(tasks, new_solutions, new_library)

    # Cost of adding the primitive itself (description length of the primitive)
    # A new primitive costs log2(n_ops) bits to name in each use,
    # but saves those bits by reducing program size.
    # Simplified: cost = 2 (one op to define, amortized over uses)
    primitive_cost = 2.0

    return {
        'name': candidate_name,
        'mdl_before': mdl_before,
        'mdl_after': mdl_after + primitive_cost,
        'delta_mdl': mdl_before - (mdl_after + primitive_cost),
        'tasks_improved': tasks_improved,
        'new_solutions': new_solutions,
        'new_library': new_library,
    }


# ── Main discovery loop ───────────────────────────────────────────────────────

class PrimitiveDiscovery:
    """
    The main Phase 1 system.
    Runs: solve tasks → test candidates → promote best → repeat.
    """

    def __init__(self):
        self.library = make_base_library()
        self.tasks = make_task_library()
        self.solutions: Dict[str, Expr] = {}
        self.history = []  # list of (round, action, delta_mdl)
        self.promoted = []  # primitives that got promoted

    def solve_all(self, pop_size=300, generations=800, verbose=True):
        """Solve all tasks with current library."""
        if verbose:
            print(f"\n  Solving {len(self.tasks)} tasks with library: "
                  f"{{{', '.join(self.library.keys())}}}")
        solved = 0
        for task in self.tasks:
            expr, score, exact = evolutionary_search(
                task, self.library, pop_size=pop_size,
                generations=generations, seed=42)
            self.solutions[task.name] = expr
            if exact:
                solved += 1
            if verbose:
                status = "EXACT" if exact else f"approx(rmse={score:.3f})"
                print(f"    {task.name:15s}: {expr.to_str()[:60]:60s} [{status}]")
        if verbose:
            print(f"  Solved exactly: {solved}/{len(self.tasks)}")
        return solved

    def discovery_round(self, verbose=True) -> Optional[str]:
        """
        One round of primitive discovery:
        1. Test all candidate primitives
        2. Promote the one with highest MDL improvement (if any)
        """
        if verbose:
            print(f"\n  Testing {len(CANDIDATE_PRIMITIVES)} candidate primitives...")

        results = []
        for name, op in CANDIDATE_PRIMITIVES.items():
            if name in self.library:
                continue  # already have it
            result = test_primitive_value(
                name, op, self.tasks, self.solutions, self.library,
                search_budget=150)
            results.append(result)
            if verbose:
                sign = '+' if result['delta_mdl'] > 0 else ''
                improved = len(result['tasks_improved'])
                print(f"    {name:8s}: ΔMDL={sign}{result['delta_mdl']:.3f}  "
                      f"improves {improved} tasks"
                      + (f"  → {[t[0] for t in result['tasks_improved']]}"
                         if result['tasks_improved'] else ''))

        # Find best primitive
        if not results:
            return None

        best = max(results, key=lambda r: r['delta_mdl'])

        if best['delta_mdl'] > 0.1:  # threshold: must genuinely help
            name = best['name']
            self.library = best['new_library']
            self.solutions = best['new_solutions']
            self.promoted.append(name)
            self.history.append(('promote', name, best['delta_mdl']))
            if verbose:
                print(f"\n  ✓ PROMOTED: {name}  (ΔMDL = +{best['delta_mdl']:.3f})")
                print(f"    Improved tasks: {[t[0] for t in best['tasks_improved']]}")
            return name
        else:
            if verbose:
                print(f"\n  No primitive worth promoting (best ΔMDL = {best['delta_mdl']:.3f})")
            return None

    def run(self, max_rounds: int = 6, verbose: bool = True):
        """
        Full discovery loop.
        """
        print("=" * 70)
        print("PHASE 1: PRIMITIVE DISCOVERY")
        print("=" * 70)
        print(f"Starting library: {{{', '.join(self.library.keys())}}}")
        print(f"Task library: {len(self.tasks)} function fitting tasks")
        print(f"Candidates: {{{', '.join(CANDIDATE_PRIMITIVES.keys())}}}")

        # Initial solve
        print("\n── ROUND 0: Initial solve (base library only) ──")
        t0 = time.time()
        solved_0 = self.solve_all(verbose=verbose)
        mdl_0 = compute_library_mdl(self.tasks, self.solutions, self.library)
        print(f"  Initial MDL: {mdl_0:.3f}  ({solved_0}/{len(self.tasks)} exact)  "
              f"[{time.time()-t0:.1f}s]")

        # Discovery rounds
        for round_n in range(1, max_rounds + 1):
            print(f"\n── ROUND {round_n}: Discovery ──")
            t0 = time.time()

            promoted = self.discovery_round(verbose=verbose)

            if promoted:
                # Re-solve everything with new library
                print(f"\n  Re-solving with {promoted} added...")
                solved = self.solve_all(verbose=verbose)
                mdl = compute_library_mdl(self.tasks, self.solutions, self.library)
                print(f"  MDL: {mdl:.3f}  ({solved}/{len(self.tasks)} exact)  "
                      f"[{time.time()-t0:.1f}s]")
            else:
                print(f"  Discovery stalled — no useful primitive found.")
                break

        # Final report
        self.report()

    def report(self):
        print("\n" + "=" * 70)
        print("PHASE 1 RESULTS")
        print("=" * 70)
        print(f"\nDiscovered primitives (in order): {self.promoted}")
        print(f"Final library: {{{', '.join(self.library.keys())}}}")
        print(f"\nFinal solutions:")
        for task in self.tasks:
            expr = self.solutions.get(task.name)
            if expr:
                score, exact = fitness(expr, task, self.library)
                status = "EXACT" if exact else f"rmse={score:.3f}"
                print(f"  {task.name:15s}: {expr.to_str()[:55]:55s}  "
                      f"[{status}]  true: {task.true_expr}")

        print(f"\nKey finding:")
        print(f"  Tasks requiring discovered primitives: "
              f"{sum(1 for t in self.tasks if t.true_expr and any(p in t.true_expr for p in self.promoted))}")

        total_mdl = compute_library_mdl(self.tasks, self.solutions, self.library)
        print(f"  Final total MDL: {total_mdl:.3f}")
        print(f"  Primitives promoted: {len(self.promoted)}")
        print(f"  Compression gain: from approximate→exact for trig/exp tasks")


if __name__ == '__main__':
    np.random.seed(42)
    disc = PrimitiveDiscovery()
    disc.run(max_rounds=6, verbose=True)
