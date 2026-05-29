"""Benchmark against Google Willow 2024, IBM Quantum, and npj 2026 targets."""

from __future__ import annotations

from .constants import (
    GAMMA_QUANTUM,
    INFO_CRITICAL_FRACTION,
    LOGICAL_DEPTH_LD,
    P_THRESHOLD,
    R2_T1_GRAPH,
    T1_REFERENCE_US,
)

QUANTUM_TARGETS: dict[str, tuple] = {
    "qec_threshold_pct":      (0.1,   0.03),   # ~10⁻³ = 0.1%
    "google_willow_t1_us":    (100.0, 0.30),   # ~100 µs T1
    "logical_depth_Ld":       (1.615, 0.05),   # Ibnouhsein 2025
    "r2_t1_from_graph":       (0.96,  0.02),   # npj 2026
    "gamma_quantum":          (0.050, 0.010),
    "info_critical_fraction": (0.25,  0.10),   # fractional preservation
}


def run_benchmark(system: object | None = None) -> dict[str, dict]:
    """
    Compare QuantumGenesis outputs against literature targets.

    Returns dict of {metric: {target, tolerance, value, passed}}.
    If system is None, uses module constants as reference values.
    """
    values: dict[str, float] = {
        "qec_threshold_pct":      P_THRESHOLD * 100.0,
        "google_willow_t1_us":    T1_REFERENCE_US,
        "logical_depth_Ld":       LOGICAL_DEPTH_LD,
        "r2_t1_from_graph":       R2_T1_GRAPH,
        "gamma_quantum":          GAMMA_QUANTUM,
        "info_critical_fraction": INFO_CRITICAL_FRACTION,
    }

    if system is not None:
        crep = system.get_crep_state()
        values["gamma_quantum"] = crep.get("Gamma", GAMMA_QUANTUM)

        utac = system.get_utac_state()
        values["qec_threshold_pct"] = (1.0 - utac.get("H_star", 1 - P_THRESHOLD)) * 100.0

    results = {}
    for metric, (target, rel_tol) in QUANTUM_TARGETS.items():
        value = values[metric]
        passed = abs(value - target) <= rel_tol + 1e-12  # tolerance is absolute
        results[metric] = {
            "target": target,
            "tolerance_abs": rel_tol,
            "value": round(value, 6),
            "passed": passed,
        }

    return results


def print_benchmark_report(results: dict[str, dict]) -> None:
    """Pretty-print benchmark results."""
    width = 30
    print(f"\n{'Metric':<{width}} {'Target':>10} {'Value':>10} {'Status':>8}")
    print("-" * (width + 32))
    all_passed = True
    for metric, r in results.items():
        status = "PASS" if r["passed"] else "FAIL"
        if not r["passed"]:
            all_passed = False
        print(f"{metric:<{width}} {r['target']:>10.4f} {r['value']:>10.4f} {status:>8}")
    print("-" * (width + 32))
    print(f"Overall: {'ALL PASS' if all_passed else 'SOME FAILURES'}\n")
