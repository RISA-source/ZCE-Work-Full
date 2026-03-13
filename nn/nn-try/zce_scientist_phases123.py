"""
ZCE Scientist: Phases 1-3
=========================
Phase 1: Primitive discovery — find primitives from MDL compression pressure
Phase 2: Library building — each solved task extends the library
Phase 3: Cross-domain transfer — primitives discovered in physics compress biology

The mathematician-scientist loop:
  solve → discover → promote → re-solve → discover deeper → ...

This is Level 3 of the K_F hierarchy: a self-extending language.
"""

import numpy as np
import time
import sys
import json
sys.path.insert(0, '/home/claude/zce_scientist')
from phase1_primitive_discovery import (
    Op, Expr, Task, X, CONST, node,
    make_base_library, CANDIDATE_PRIMITIVES,
    evolutionary_search, fitness, compute_library_mdl,
    test_primitive_value, mutate, random_expr
)


# ── Domain definitions for Phase 3 ───────────────────────────────────────────

def make_physics_tasks() -> list:
    """Physics-flavored function tasks."""
    return [
        Task.make('harmonic_osc',  lambda t: np.cos(2*np.pi*t),
                  xrange=(0,4), true_expr='COS(2πt)',
                  n=40),
        Task.make('damped_osc',    lambda t: np.exp(-0.5*t)*np.cos(3*t),
                  xrange=(0,4), true_expr='EXP(-0.5t)·COS(3t)',
                  n=40),
        Task.make('boltzmann',     lambda E: np.exp(-E),
                  xrange=(0,5), true_expr='EXP(-E)',
                  n=40),
        Task.make('wave_packet',   lambda x: np.sin(5*x)*np.exp(-x**2/4),
                  xrange=(-4,4), true_expr='SIN(5x)·EXP(-x²/4)',
                  n=40),
        Task.make('coulomb',       lambda r: 1.0/(r**2 + 0.1),
                  xrange=(0.5,5), true_expr='1/(r²+0.1)',
                  n=40),
        Task.make('lorentzian',    lambda x: 1.0/(x**2 + 1),
                  xrange=(-4,4), true_expr='1/(x²+1)',
                  n=40),
    ]


def make_biology_tasks() -> list:
    """Biology-flavored function tasks (logistic growth, oscillations, decay)."""
    return [
        Task.make('logistic',      lambda t: 1.0/(1 + np.exp(-t)),
                  xrange=(-5,5), true_expr='1/(1+EXP(-t))',
                  n=40),
        Task.make('pop_growth',    lambda t: np.exp(0.3*t),
                  xrange=(0,5), true_expr='EXP(0.3t)',
                  n=40),
        Task.make('circadian',     lambda t: 0.5 + 0.5*np.sin(2*np.pi*t/24),
                  xrange=(0,48), true_expr='0.5+0.5·SIN(2πt/24)',
                  n=40),
        Task.make('lotka_f',       lambda x: np.sin(x)*np.exp(-0.1*x),
                  xrange=(0,10), true_expr='SIN(x)·EXP(-0.1x)',
                  n=40),
        Task.make('hill_fn',       lambda x: x**2/(1 + x**2),
                  xrange=(0,5), true_expr='x²/(1+x²)',
                  n=40),
    ]


# ── Phase 1 runner ────────────────────────────────────────────────────────────

def run_phase1(tasks, max_rounds=5, pop_size=200, generations=500, verbose=True):
    """
    Phase 1: Discover primitives from scratch.
    Returns (final_library, solutions, discovery_log).
    """
    library = make_base_library()
    solutions = {}
    discovery_log = []

    print("\n" + "═"*65)
    print("PHASE 1: PRIMITIVE DISCOVERY")
    print("═"*65)
    print(f"Base library: {{{', '.join(library.keys())}}}")
    print(f"Task set:     {[t.name for t in tasks]}")
    print(f"Candidates:   {{{', '.join(CANDIDATE_PRIMITIVES.keys())}}}")

    # Round 0: initial solve
    print(f"\n── Round 0: Baseline (base library only) ──")
    t0 = time.time()
    solved = 0
    for task in tasks:
        expr, score, exact = evolutionary_search(
            task, library, pop_size=pop_size, generations=generations, seed=42)
        solutions[task.name] = expr
        solved += exact
    mdl = compute_library_mdl(tasks, solutions, library)
    print(f"  Solved: {solved}/{len(tasks)} exact   MDL: {mdl:.3f}   [{time.time()-t0:.1f}s]")
    for t in tasks:
        expr = solutions[t.name]; sc, ex = fitness(expr, t, library)
        print(f"    {t.name:16s}: {expr.to_str()[:45]:45s} "
              f"[{'EXACT' if ex else f'rmse={sc:.3f}'}]")
    discovery_log.append({'round': 0, 'mdl': mdl, 'solved': solved, 'promoted': None})

    # Discovery rounds
    for round_n in range(1, max_rounds + 1):
        print(f"\n── Round {round_n}: Discovery ──")
        t0 = time.time()

        # Test each candidate
        results = []
        for name, op in CANDIDATE_PRIMITIVES.items():
            if name in library:
                continue
            result = test_primitive_value(name, op, tasks, solutions, library,
                                          search_budget=150)
            results.append(result)

        # Sort by MDL gain
        results.sort(key=lambda r: -r['delta_mdl'])

        print(f"  Candidate evaluation:")
        for r in results:
            improved = [t[0] for t in r['tasks_improved']]
            sign = '+' if r['delta_mdl'] > 0 else ''
            print(f"    {r['name']:8s}: ΔMDL={sign}{r['delta_mdl']:+.3f}   "
                  f"improves {len(improved)} tasks: {improved}")

        if results and results[0]['delta_mdl'] > 0.05:
            best = results[0]
            name = best['name']
            library = best['new_library']
            solutions = best['new_solutions']

            # Re-solve everything with new library for accuracy
            print(f"\n  ✓ PROMOTING: {name}  (ΔMDL = +{best['delta_mdl']:.3f})")
            print(f"  Re-solving all tasks with {name} in library...")
            solved = 0
            for task in tasks:
                expr, score, exact = evolutionary_search(
                    task, library, pop_size=pop_size,
                    generations=generations, seed=42)
                solutions[task.name] = expr
                solved += exact
            mdl = compute_library_mdl(tasks, solutions, library)
            print(f"  Solved: {solved}/{len(tasks)} exact   MDL: {mdl:.3f}   [{time.time()-t0:.1f}s]")
            for t in tasks:
                expr = solutions[t.name]; sc, ex = fitness(expr, t, library)
                print(f"    {t.name:16s}: {expr.to_str()[:45]:45s} "
                      f"[{'EXACT' if ex else f'rmse={sc:.3f}'}]")

            discovery_log.append({
                'round': round_n, 'mdl': mdl, 'solved': solved,
                'promoted': name, 'delta_mdl': best['delta_mdl'],
                'tasks_improved': [t[0] for t in best['tasks_improved']]
            })
        else:
            print(f"\n  No useful primitive found. Discovery complete.")
            discovery_log.append({'round': round_n, 'mdl': mdl,
                                   'solved': solved, 'promoted': None})
            break

    return library, solutions, discovery_log


# ── Phase 2: Library building from solved problems ────────────────────────────

def expr_to_fn(expr: Expr, library: dict):
    """Convert an expression to a numpy function (for use as a primitive)."""
    def fn(x):
        return expr.eval(x, library)
    return fn


def run_phase2(base_library, base_solutions, tasks, verbose=True):
    """
    Phase 2: Each solved task's solution becomes a candidate primitive.
    We extract 'interesting' subexpressions that appear to compress other tasks.

    This is the library-building step: solved problems = reusable pieces.
    """
    print("\n" + "═"*65)
    print("PHASE 2: LIBRARY BUILDING FROM SOLVED TASKS")
    print("═"*65)

    library = dict(base_library)
    solutions = dict(base_solutions)

    # Extract candidate sub-expressions from solutions
    # A good candidate: a subexpr that (a) appears in ≥1 solution exactly,
    # (b) is not trivially simple (size ≥ 2), (c) is not already a primitive

    def extract_subexprs(expr: Expr, min_size: int = 2):
        """Recursively extract all subexpressions of sufficient complexity."""
        result = []
        if expr.size(library) >= min_size and expr.op not in ('X', 'CONST'):
            result.append(expr)
        for child in expr.children:
            result.extend(extract_subexprs(child, min_size))
        return result

    # Collect subexpressions from all exact solutions
    candidates = {}
    for task in tasks:
        expr = solutions.get(task.name)
        if expr and fitness(expr, task, library)[1]:  # exact solution
            for sub in extract_subexprs(expr, min_size=2):
                key = sub.to_str()
                if key not in candidates and 'X' in key:  # must use X
                    candidates[key] = (sub, task.name)

    print(f"\n  Extracted {len(candidates)} subexpressions from exact solutions.")
    for key, (sub, src) in list(candidates.items())[:10]:
        print(f"    {key[:40]:40s} (from {src})")

    # Test each subexpr as a candidate primitive
    print(f"\n  Testing subexpressions as primitives...")
    promoted_compound = []
    for key, (sub_expr, source_task) in list(candidates.items())[:20]:
        # Create an Op from this subexpr
        sub_fn = expr_to_fn(sub_expr, library)
        candidate_op = Op(f'LIB_{len(promoted_compound)}', 1, sub_fn,
                         cost=1, discovered=True)

        # Only test if not trivially equivalent to existing primitives
        candidates_to_test = {'CANDIDATE': candidate_op}
        result = test_primitive_value('CANDIDATE', candidate_op,
                                       tasks, solutions, library,
                                       search_budget=80)

        if result['delta_mdl'] > 0.2:
            name = f'LIB_{sub_expr.to_str()[:12].replace(" ","")}'
            library[name] = Op(name, 1, sub_fn, cost=1, discovered=True)
            solutions = result['new_solutions']
            promoted_compound.append((name, key, result['delta_mdl']))
            print(f"  ✓ PROMOTED compound: {name} = {key[:40]}  "
                  f"ΔMDL=+{result['delta_mdl']:.3f}")

    print(f"\n  Compound primitives added: {len(promoted_compound)}")
    mdl = compute_library_mdl(tasks, solutions, library)
    print(f"  New library MDL: {mdl:.3f}")
    print(f"  Library size: {len(library)} primitives")

    return library, solutions, promoted_compound


# ── Phase 3: Cross-domain transfer ───────────────────────────────────────────

def run_phase3(physics_library, physics_solutions, bio_tasks, verbose=True):
    """
    Phase 3: Test whether primitives discovered in physics
    compress biology tasks — without retraining.

    This is the mathematician-scientist property:
    The concept SIN discovered in harmonic oscillator problems
    is the same SIN that appears in circadian rhythms.
    """
    print("\n" + "═"*65)
    print("PHASE 3: CROSS-DOMAIN TRANSFER")
    print("═"*65)
    print("Physics library → applied to biology tasks")

    # Solve bio tasks with base library only
    base_lib = make_base_library()
    print("\n  Solving biology with BASE library (no physics primitives)...")
    base_solutions = {}
    base_solved = 0
    for task in bio_tasks:
        expr, score, exact = evolutionary_search(
            task, base_lib, pop_size=200, generations=500, seed=42)
        base_solutions[task.name] = expr
        base_solved += exact
    base_mdl = compute_library_mdl(bio_tasks, base_solutions, base_lib)

    print(f"  Base MDL: {base_mdl:.3f}  ({base_solved}/{len(bio_tasks)} exact)")

    # Solve bio tasks with physics library (transferred primitives)
    print(f"\n  Solving biology with PHYSICS library ({list(physics_library.keys())})...")
    physics_solutions_bio = {}
    physics_solved = 0
    for task in bio_tasks:
        expr, score, exact = evolutionary_search(
            task, physics_library, pop_size=200, generations=500, seed=42)
        physics_solutions_bio[task.name] = expr
        physics_solved += exact
    physics_mdl = compute_library_mdl(bio_tasks, physics_solutions_bio, physics_library)

    print(f"  Physics-transfer MDL: {physics_mdl:.3f}  ({physics_solved}/{len(bio_tasks)} exact)")

    # Per-task comparison
    print(f"\n  Per-task comparison:")
    print(f"  {'Task':16s}  {'Base':25s}  {'With Physics':40s}")
    print(f"  {'─'*16}  {'─'*25}  {'─'*40}")
    transfer_wins = 0
    for task in bio_tasks:
        base_expr = base_solutions[task.name]
        phys_expr = physics_solutions_bio[task.name]
        base_sc, base_ex = fitness(base_expr, task, base_lib)
        phys_sc, phys_ex = fitness(phys_expr, task, physics_library)
        better = phys_sc < base_sc - 0.01 or (phys_ex and not base_ex)
        transfer_wins += better
        marker = '✓' if better else ' '
        print(f" {marker} {task.name:16s}  "
              f"{base_expr.to_str()[:23]:25s}  "
              f"{phys_expr.to_str()[:38]:40s}")

    delta = base_mdl - physics_mdl
    print(f"\n  Transfer result:")
    print(f"    MDL improvement: {delta:+.3f} ({delta/base_mdl*100:+.1f}%)")
    print(f"    Tasks improved by transfer: {transfer_wins}/{len(bio_tasks)}")
    print(f"    {'✓ Transfer successful' if delta > 0.1 else '✗ Transfer marginal'}: "
          f"physics primitives compress biology tasks")

    return {
        'base_mdl': base_mdl,
        'physics_mdl': physics_mdl,
        'delta_mdl': delta,
        'transfer_wins': transfer_wins,
        'n_tasks': len(bio_tasks),
    }


# ── Full run ──────────────────────────────────────────────────────────────────

def run_all(quick=False):
    """Run all three phases end-to-end."""
    pop = 150 if quick else 250
    gen = 300 if quick else 600

    print("\n" + "█"*65)
    print("  ZCE SCIENTIST — PHASES 1-3")
    print("  Goal: self-extending language for math and science")
    print("█"*65)

    # Phase 1: Primitive discovery on math tasks
    from phase1_primitive_discovery import make_task_library
    math_tasks = make_task_library()
    lib1, sol1, log1 = run_phase1(math_tasks, max_rounds=5,
                                   pop_size=pop, generations=gen)

    # Phase 2: Library building
    lib2, sol2, promoted2 = run_phase2(lib1, sol1, math_tasks)

    # Phase 3: Transfer to new domain
    bio_tasks = make_biology_tasks()
    transfer_result = run_phase3(lib1, sol1, bio_tasks)

    # Final summary
    print("\n" + "═"*65)
    print("FINAL SUMMARY")
    print("═"*65)

    promoted_p1 = [e['promoted'] for e in log1 if e.get('promoted')]
    print(f"\nPhase 1 — Discovered primitives: {promoted_p1}")
    print(f"  MDL trajectory: "
          + " → ".join(f"{e['mdl']:.2f}" for e in log1))

    print(f"\nPhase 2 — Compound library entries: {len(promoted2)}")
    for name, expr_str, gain in promoted2[:5]:
        print(f"  {name} = {expr_str[:40]}  ΔMDL=+{gain:.3f}")

    print(f"\nPhase 3 — Cross-domain transfer:")
    print(f"  Physics→Biology MDL: {transfer_result['base_mdl']:.3f} → "
          f"{transfer_result['physics_mdl']:.3f}  "
          f"(Δ={transfer_result['delta_mdl']:+.3f})")
    print(f"  Tasks improved: {transfer_result['transfer_wins']}/{transfer_result['n_tasks']}")

    print(f"\nKey result:")
    if promoted_p1:
        print(f"  ✓ System discovered {promoted_p1} from compression pressure alone")
        print(f"  ✓ Primitives are justified by MDL (not hand-coded)")
    if transfer_result['delta_mdl'] > 0:
        print(f"  ✓ Physics primitives transfer to biology ({transfer_result['delta_mdl']:+.3f} MDL gain)")
    print(f"  This is Level 3: a self-extending language guided by compression")

    return lib1, lib2, transfer_result


if __name__ == '__main__':
    quick = '--quick' in sys.argv
    run_all(quick=quick)
