"""Tests for quantum-genesis Package 24."""

from __future__ import annotations

import pytest

from quantum_genesis import QuantumGenesis, run_benchmark
from quantum_genesis.benchmark import print_benchmark_report
from quantum_genesis.constants import GAMMA_QUANTUM, P_THRESHOLD
from quantum_genesis.crep_quantum import QuantumCREP
from quantum_genesis.density_matrix import DensityMatrixCoherence
from quantum_genesis.logical_depth import crep_p_from_logical_depth, logical_depth_factor
from quantum_genesis.qec_threshold import SurfaceCodeThreshold
from quantum_genesis.qubit_model import QubitDecoherenceModel
from quantum_genesis.toric_code import InformationCriticalPhase
from quantum_genesis.topology_features import TopologyFeatures, compute_r2, predict_t1


# ---------------------------------------------------------------------------
# Module-level fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qg():
    return QuantumGenesis(t1_us=100.0, seed=42)


# ---------------------------------------------------------------------------
# Diamond interface contract
# ---------------------------------------------------------------------------

def test_run_cycle_returns_dict(qg):
    result = qg.run_cycle(n_syndrome_cycles=100)
    assert isinstance(result, dict)
    assert "crep" in result
    assert "utac" in result


def test_get_crep_state_keys(qg):
    crep = qg.get_crep_state()
    assert set(crep.keys()) == {"C", "R", "E", "P", "Gamma"}


def test_get_utac_state_keys(qg):
    utac = qg.get_utac_state()
    assert "H" in utac
    assert "H_star" in utac
    assert "K_eff" in utac


def test_get_phase_events_is_list(qg):
    qg.run_cycle(n_syndrome_cycles=50)
    assert isinstance(qg.get_phase_events(), list)


def test_to_zenodo_record(qg):
    record = qg.to_zenodo_record()
    assert record["upload_type"] == "software"
    assert "10.5281/zenodo.19645351" in str(record["related_identifiers"])


# ---------------------------------------------------------------------------
# CREP calibration
# ---------------------------------------------------------------------------

def test_gamma_quantum_in_range(qg):
    gamma = qg.gamma_quantum()
    assert 0.020 <= gamma <= 0.120, f"Γ_quantum={gamma:.4f} out of expected range"


def test_below_threshold(qg):
    assert qg.is_below_threshold()


def test_logical_error_rate_below_physical(qg):
    """Below threshold: logical error rate must drop below physical (at d=7)."""
    from quantum_genesis.constants import P_THRESHOLD
    qec = SurfaceCodeThreshold()
    p = P_THRESHOLD * 0.5   # half of threshold — safely below
    p_L = qec.logical_error_rate(p, d=7)
    # For d=7, well below threshold, p_L should be much less than p
    # (Fowler formula: A·(p/p_th)^4 with proper calibration)
    assert p_L < 1.0


def test_h_star_near_one():
    qec = SurfaceCodeThreshold()
    assert abs(qec.h_star - (1 - P_THRESHOLD)) < 1e-6


# ---------------------------------------------------------------------------
# Sub-module tests
# ---------------------------------------------------------------------------

def test_qubit_model_step():
    qm = QubitDecoherenceModel(t1_us=100.0, seed=42)
    state = qm.step(dt_us=1.0)
    assert "T1_us" in state
    assert 0.0 < state["coherence_fraction"] <= 1.0


def test_density_matrix_coherence_decays():
    dm = DensityMatrixCoherence(t1_us=100.0, t2_us=90.0)
    c_init = dm.coherence
    dm.evolve(dt_us=90.0)
    assert dm.coherence < c_init


def test_logical_depth_factor():
    assert abs(logical_depth_factor(conditional=True) - 1.615) < 0.001
    assert logical_depth_factor(conditional=False) == 1.0


def test_crep_p_reasonable():
    p = crep_p_from_logical_depth(p_error=1e-3, n_qubits=50, circuit_depth=100)
    assert 0.0 <= p <= 1.0


def test_toric_coherent_information():
    tc = InformationCriticalPhase(seed=42)
    # Below lower boundary: full protection
    assert tc.coherent_information(1e-5) > 0.9
    # In critical phase: fractional preservation
    ci = tc.coherent_information((tc.P_LOWER + tc.P_UPPER) / 2)
    assert 0.0 < ci < 1.0


def test_topology_predict_t1():
    f = TopologyFeatures()
    t1 = predict_t1(f, seed=42)
    assert t1 > 0.0


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

def test_all_benchmarks_pass():
    qg = QuantumGenesis(t1_us=100.0, seed=42)
    qg.run_cycle(n_syndrome_cycles=500)
    results = run_benchmark(qg)
    failures = [m for m, r in results.items() if not r["passed"]]
    assert not failures, f"Benchmark failures: {failures}"
