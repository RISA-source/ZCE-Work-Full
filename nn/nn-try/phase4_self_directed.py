"""
Phase 4: Self-Directed Candidate Generation
============================================
The system proposes its OWN primitive candidates from scratch.
No human-provided candidate list.

Mechanism:
  1. Solve all tasks with current library
  2. On unsolved tasks: fit parametric families to task values
     - sinusoidal: A*sin(w*x + phi)
     - exponential: A*exp(b*x)
     - logarithmic: A*log(|x| + c)
     - power: A*x^n
  3. The family that best fits the MOST unsolved tasks = proposed primitive
  4. Construct a concrete Op from the winning family
  5. Test with MDL criterion (same as Phase 1)
  6. Promote if ΔMDL > threshold

This is unsupervised primitive proposal. The system "sees" what it cannot
explain and asks: what kind of function would explain it?
"""

import numpy as np
import sys
import time
from numpy.fft import fft, fftfreq
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
sys.path.insert(0, '/home/claude/zce_scientist')
from phase1_primitive_discovery import (
    Op, Expr, Task, X, CONST, node,
    make_base_library, make_task_library,
    evolutionary_search, fitness, compute_library_mdl,
    test_primitive_value, CANDIDATE_PRIMITIVES
)


# ── Parametric family fitting ─────────────────────────────────────────────────

def fit_sinusoidal(x: np.ndarray, y: np.ndarray) -> Tuple[float, dict]:
    """Fit A*sin(w*x + phi) via FFT. Returns (rmse, params)."""
    n = len(x); dx = x[1] - x[0]
    freqs = fftfreq(n, dx)
    spectrum = np.abs(fft(y))
    # Find dominant non-DC frequency
    idx = np.argmax(spectrum[1:n//2]) + 1
    w = 2 * np.pi * abs(freqs[idx])
    if w < 1e-6:
        w = 1.0
    A = np.std(y) * np.sqrt(2)
    # Scan phases
    best_rmse, best_phi = np.inf, 0.0
    for phi in np.linspace(0, 2*np.pi, 40):
        pred = A * np.sin(w*x + phi)
        rmse = np.sqrt(np.mean((y - pred)**2))
        if rmse < best_rmse:
            best_rmse = rmse; best_phi = phi
    return best_rmse, {'A': A, 'w': w, 'phi': best_phi, 'family': 'sinusoidal'}


def fit_exponential(x: np.ndarray, y: np.ndarray) -> Tuple[float, dict]:
    """Fit A*exp(b*x) by linear regression in log space."""
    mask = np.abs(y) > 1e-3
    if mask.sum() < 6:
        return np.inf, {}
    try:
        coeffs = np.polyfit(x[mask], np.log(np.abs(y[mask]) + 1e-10), 1)
        b, logA = coeffs
        A = np.exp(logA) * np.sign(y[mask].mean())
        pred = A * np.exp(np.clip(b * x, -15, 15))
        rmse = np.sqrt(np.mean((y - pred)**2))
        return rmse, {'A': A, 'b': b, 'family': 'exponential'}
    except:
        return np.inf, {}


def fit_logarithmic(x: np.ndarray, y: np.ndarray) -> Tuple[float, dict]:
    """Fit A*log(|x| + c)."""
    best_rmse, best_params = np.inf, {}
    for c in [0.1, 0.5, 1.0, 2.0]:
        log_x = np.log(np.abs(x) + c)
        # Linear regression: y = A*log_x + B
        A, B = np.polyfit(log_x, y, 1)
        pred = A * log_x + B
        rmse = np.sqrt(np.mean((y - pred)**2))
        if rmse < best_rmse:
            best_rmse = rmse
            best_params = {'A': A, 'B': B, 'c': c, 'family': 'logarithmic'}
    return best_rmse, best_params


def fit_power(x: np.ndarray, y: np.ndarray) -> Tuple[float, dict]:
    """Fit A*|x|^n for non-integer n."""
    mask = np.abs(x) > 0.1
    if mask.sum() < 6:
        return np.inf, {}
    best_rmse, best_n = np.inf, 1.0
    for n in [0.5, 1.5, 2.5, 3.0, 3.5, -0.5, -1.0, -2.0]:
        try:
            px = np.sign(x[mask]) * np.abs(x[mask])**n
            A = np.dot(px, y[mask]) / (np.dot(px, px) + 1e-10)
            pred = np.zeros_like(y)
            pred[mask] = A * px
            rmse = np.sqrt(np.mean((y - pred)**2))
            if rmse < best_rmse:
                best_rmse = rmse; best_n = n
                best_params = {'A': A, 'n': n, 'family': 'power'}
        except:
            continue
    return best_rmse, best_params if best_rmse < np.inf else {}


FAMILIES = {
    'sinusoidal':  fit_sinusoidal,
    'exponential': fit_exponential,
    'logarithmic': fit_logarithmic,
    'power':       fit_power,
}

# Map family name → Op constructor
def family_to_op(family_name: str, params: dict, name: str) -> Op:
    """
    Convert a winning family to a canonical Op.

    Critical design decision: we generate the CANONICAL form of the primitive,
    not the parameterized fit. The w, b, c parameters are EVIDENCE that this
    family is needed — but the primitive we add is the pure version.
    Composition handles scaling: sin(2x) = SIN(ADD(x,x)), not SIN_w=2(x).

    This is how mathematics works: we add 'sin' not 'sin_with_period_6.28'.
    """
    if family_name == 'sinusoidal':
        # Canonical: sin(x). The system can compose to get sin(wx+phi).
        return Op(name, 1, lambda x: np.sin(x), cost=1, discovered=True)

    elif family_name == 'exponential':
        # Canonical: exp(x). System composes for exp(-x), exp(bx), etc.
        return Op(name, 1, lambda x: np.exp(np.clip(x, -10, 10)),
                 cost=1, discovered=True)

    elif family_name == 'logarithmic':
        # Canonical: log(|x| + 1). Small offset for stability.
        return Op(name, 1, lambda x: np.log(np.abs(x) + 1.0),
                 cost=1, discovered=True)

    elif family_name == 'power':
        n = params.get('n', 2.0)
        # Round to nearest 0.5 for interpretability
        n_canonical = round(n * 2) / 2
        if abs(n_canonical - 2.0) < 0.1:
            return Op(name, 1, lambda x: x**2, cost=1, discovered=True)
        elif abs(n_canonical - 0.5) < 0.1:
            return Op(name, 1, lambda x: np.sqrt(np.abs(x)), cost=1, discovered=True)
        elif abs(n_canonical - (-1.0)) < 0.1:
            return Op(name, 1, lambda x: 1.0/(np.abs(x)+1e-10), cost=1, discovered=True)
        else:
            def fn(x, _n=n_canonical): return np.sign(x)*np.abs(x)**_n
            return Op(name, 1, fn, cost=1, discovered=True)

    else:
        return Op(name, 1, lambda x: x, cost=1, discovered=True)


# ── Candidate generator ───────────────────────────────────────────────────────

def generate_candidates(tasks: List[Task], solutions: Dict, library: Dict,
                         min_votes: int = 2, verbose: bool = True) -> List[Tuple[str, Op, dict]]:
    """
    Look at all unsolved tasks.
    For each unsolved task, fit all parametric families.
    The family with the most votes = proposed primitive.

    Returns list of (name, op, metadata) sorted by votes.
    """
    # Find unsolved tasks and their best current approximation
    unsolved = []
    for task in tasks:
        expr = solutions.get(task.name)
        if expr is None:
            unsolved.append((task, task.y))
            continue
        sc, ex = fitness(expr, task, library)
        if not ex:
            unsolved.append((task, task.y))

    if verbose:
        print(f"  Unsolved tasks ({len(unsolved)}): {[t.name for t, _ in unsolved]}")

    if len(unsolved) < 2:
        return []

    # Fit each family to each unsolved task
    family_scores = {f: [] for f in FAMILIES}
    family_params_by_task = {f: {} for f in FAMILIES}

    for task, y in unsolved:
        best_family = None; best_rmse = np.inf
        task_results = {}
        for fname, ffn in FAMILIES.items():
            rmse, params = ffn(task.x, y)
            task_results[fname] = (rmse, params)
            if rmse < best_rmse:
                best_rmse = rmse; best_family = fname
        # Vote for best family on this task
        for fname in FAMILIES:
            rmse, params = task_results[fname]
            family_scores[fname].append((task.name, rmse))
            family_params_by_task[fname][task.name] = params

    # Count wins and compute aggregate fit quality
    results = []
    for fname in FAMILIES:
        scores = family_scores[fname]
        # How many tasks does this family win?
        wins = sum(
            1 for t_name, rmse in scores
            if rmse <= min(
                family_scores[other][i][1]
                for other, other_scores in family_scores.items()
                for j, (tn, _) in enumerate(other_scores) if tn == t_name
                for i in [j]
            )
        )
        avg_rmse = np.mean([s[1] for s in scores])
        best_params = {}
        # Collect best-fit params across tasks that this family wins
        for t_name, rmse in scores:
            p = family_params_by_task[fname].get(t_name, {})
            if p:
                best_params = p  # use last winning params as representative

        results.append({
            'family': fname,
            'wins': wins,
            'avg_rmse': avg_rmse,
            'representative_params': best_params,
        })

    results.sort(key=lambda r: (-r['wins'], r['avg_rmse']))

    if verbose:
        print(f"  Family voting results:")
        for r in results:
            print(f"    {r['family']:12s}: wins={r['wins']}  avg_rmse={r['avg_rmse']:.3f}")

    # Convert top families to candidate Ops
    candidates = []
    for r in results:
        if r['wins'] >= min_votes:
            name = f"DISC_{r['family'].upper()[:6]}_{len(candidates)}"
            op = family_to_op(r['family'], r['representative_params'], name)
            candidates.append((name, op, r))
            if verbose:
                print(f"  → Proposing candidate: {name} (family={r['family']}, "
                      f"wins={r['wins']})")

    return candidates


# ── Self-directed discovery loop ──────────────────────────────────────────────

def run_self_directed(tasks: List[Task] = None, max_rounds: int = 6,
                       pop_size: int = 200, generations: int = 500,
                       verbose: bool = True) -> Dict:
    """
    Full self-directed discovery loop.
    The system generates its OWN candidate primitives.
    No human-provided candidate list.
    """
    if tasks is None:
        tasks = make_task_library()

    library = make_base_library()
    solutions = {}
    history = []

    print("\n" + "█"*65)
    print("  PHASE 4: SELF-DIRECTED CANDIDATE GENERATION")
    print("  No human-provided candidate list.")
    print("  System proposes primitives from unsolved task structure.")
    print("█"*65)
    print(f"\nStarting library: {{{', '.join(library.keys())}}}")

    # Initial solve
    print(f"\n── Round 0: Baseline ──")
    t0 = time.time()
    solved = 0
    for task in tasks:
        expr, score, exact = evolutionary_search(
            task, library, pop_size=pop_size, generations=generations, seed=42)
        solutions[task.name] = expr
        solved += exact
    mdl = compute_library_mdl(tasks, solutions, library)
    print(f"  Solved: {solved}/{len(tasks)} exact   MDL: {mdl:.3f}   [{time.time()-t0:.1f}s]")

    history.append({'round': 0, 'mdl': mdl, 'solved': solved,
                    'promoted': None, 'proposed': None})

    for round_n in range(1, max_rounds + 1):
        print(f"\n── Round {round_n}: Self-directed discovery ──")
        t0 = time.time()

        # Step 1: Generate candidates from unsolved task structure
        print(f"  Step 1: Generating candidates from {len(tasks)-solved} unsolved tasks...")
        candidates = generate_candidates(tasks, solutions, library,
                                          min_votes=2, verbose=verbose)

        if not candidates:
            print(f"  No candidates proposed. Discovery complete.")
            break

        # Step 2: Test each candidate with MDL criterion
        print(f"\n  Step 2: MDL evaluation of {len(candidates)} proposed candidates...")
        mdl_results = []
        for cname, cop, cmeta in candidates:
            result = test_primitive_value(
                cname, cop, tasks, solutions, library, search_budget=200)
            mdl_results.append((cname, cop, cmeta, result))
            sign = '+' if result['delta_mdl'] > 0 else ''
            print(f"    {cname:20s} (family={cmeta['family']:12s}): "
                  f"ΔMDL={sign}{result['delta_mdl']:+.3f}  "
                  f"improves {len(result['tasks_improved'])} tasks")

        # Step 3: Promote best if ΔMDL > threshold
        mdl_results.sort(key=lambda x: -x[3]['delta_mdl'])
        best_name, best_op, best_meta, best_result = mdl_results[0]

        if best_result['delta_mdl'] > 0.05:
            library = best_result['new_library']
            solutions = best_result['new_solutions']

            print(f"\n  ✓ PROMOTING: {best_name}")
            print(f"    Family: {best_meta['family']}")
            print(f"    ΔMDL: +{best_result['delta_mdl']:.3f}")
            print(f"    Improved tasks: {[t[0] for t in best_result['tasks_improved']]}")

            # Re-solve with new primitive
            print(f"  Re-solving all tasks with {best_name}...")
            solved = 0
            for task in tasks:
                expr, score, exact = evolutionary_search(
                    task, library, pop_size=pop_size,
                    generations=generations, seed=42)
                solutions[task.name] = expr
                solved += exact
            mdl = compute_library_mdl(tasks, solutions, library)
            print(f"  Solved: {solved}/{len(tasks)} exact   MDL: {mdl:.3f}   [{time.time()-t0:.1f}s]")

            history.append({
                'round': round_n, 'mdl': mdl, 'solved': solved,
                'promoted': best_name, 'proposed': best_meta['family'],
                'delta_mdl': best_result['delta_mdl'],
                'tasks_improved': [t[0] for t in best_result['tasks_improved']],
            })
        else:
            print(f"\n  No candidate worth promoting. Best ΔMDL={best_result['delta_mdl']:.3f}")
            history.append({'round': round_n, 'mdl': mdl, 'solved': solved,
                             'promoted': None, 'proposed': best_meta['family']})
            break

    # Final report
    print("\n" + "═"*65)
    print("PHASE 4 RESULTS")
    print("═"*65)

    promoted = [h for h in history if h.get('promoted')]
    print(f"\nPrimitives self-generated: {[h['promoted'] for h in promoted]}")
    print(f"From families: {[h['proposed'] for h in promoted]}")
    mdl_trace = ' → '.join(f'{h["mdl"]:.3f}' for h in history)
    print(f"MDL: {mdl_trace}")
    print(f"Solved: {history[0]['solved']} → {history[-1]['solved']}/{len(tasks)}")

    print(f"\nFinal solutions:")
    for task in tasks:
        expr = solutions.get(task.name)
        if expr:
            sc, ex = fitness(expr, task, library)
            print(f"  {task.name:16s}: {expr.to_str()[:50]:50s} "
                  f"[{'EXACT' if ex else f'rmse={sc:.3f}'}]")

    print(f"\nKey finding:")
    if promoted:
        print(f"  ✓ System self-generated {len(promoted)} primitive(s)")
        print(f"  ✓ Proposed by examining unsolved task structure (no human list)")
        print(f"  ✓ Promoted by MDL criterion (compression genuinely improves)")
        for h in promoted:
            print(f"  ✓ '{h['promoted']}' ({h['proposed']} family) → "
                  f"{h['solved']}/{len(tasks)} exact, ΔMDL=+{h['delta_mdl']:.3f}")
    else:
        print(f"  Discovery stalled — search budget or threshold needs tuning")

    return {
        'library': library,
        'solutions': solutions,
        'history': history,
        'promoted': [h for h in history if h.get('promoted')],
    }


if __name__ == '__main__':
    import sys
    quick = '--quick' in sys.argv
    pop = 120 if quick else 200
    gen = 250 if quick else 500
    tasks = make_task_library()
    result = run_self_directed(tasks, max_rounds=5, pop_size=pop, generations=gen)
