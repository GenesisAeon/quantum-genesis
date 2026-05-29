"""
QuantumGenesis — Diamond interface for Package 24.

Models qubit decoherence as a UTAC threshold system, coupling the QEC
threshold theorem to the CREP framework.

References:
  Ibnouhsein 2025  — DOI: 10.1007/s10701-025-00883-w
  npj QI 2026      — DOI: 10.1038/s41534-026-01199-x
  Vijay & Lee 2026 — Information critical phase in decohered Toric codes
  Google Willow 2024 — below-threshold QEC demonstrated
"""

from __future__ import annotations

import math
import random
from datetime import UTC, datetime

from .constants import (
    K_COHERENCE,
    R_IMPROVEMENT,
    SEED,
    SIGMA,
    T1_REFERENCE_US,
)
from .crep_quantum import QuantumCREP
from .density_matrix import DensityMatrixCoherence
from .qec_threshold import SurfaceCodeThreshold
from .qubit_model import QubitDecoherenceModel
from .toric_code import InformationCriticalPhase  # noqa: F401 (available for notebook use)


class QuantumGenesis:
    """
    Diamond interface for Package 24 — Qubit Decoherence as UTAC System.

    UTAC mapping:
      H(t) = coherence fraction = (1 - p_error) ∈ [0, 1]
      K    = 1.0 (perfect coherence)
      H*   = 1 - p_threshold ≈ 0.999
      r    = coherence improvement rate per generation (~0.10)
      σ    = 2.2 (universal CREP coupling)
      Γ    ≈ 0.050 (quantum fragile — most sensitive UTAC system in atlas)
    """

    PACKAGE_ID: int = 24
    DOMAIN: str = "quantum-physics"
    SCALE: str = "mesoscopic"
    REFERENCE_DOI: str = "10.1007/s10701-025-00883-w"

    def __init__(
        self,
        t1_us: float = T1_REFERENCE_US,
        p_error: float | None = None,
        seed: int = SEED,
    ) -> None:
        self._rng = random.Random(seed)
        self._seed = seed

        self._qubit = QubitDecoherenceModel(t1_us=t1_us, seed=seed)
        self._dm = DensityMatrixCoherence(t1_us=t1_us, t2_us=t1_us * 0.9)
        self._qec = SurfaceCodeThreshold(seed=seed)
        self._crep_calc = QuantumCREP(self._qec)

        # Current physical error rate
        self._p_error: float = p_error if p_error is not None else self._qubit.error_rate
        self._phase_events: list[dict] = []
        self._cycle_results: list[dict] = []

    # ------------------------------------------------------------------
    # Diamond contract
    # ------------------------------------------------------------------

    def run_cycle(self, n_syndrome_cycles: int = 1000) -> dict:
        """
        Simulate n_syndrome_cycles of QEC operation.

        Each syndrome cycle: dt = t_gate duration.
        Returns summary of the run including Γ, phase events, UTAC state.
        """
        self._phase_events.clear()
        dt_us = self._qubit.t_gate_ns * 1e-3   # gate time in µs

        crep_history: list[dict] = []
        utac_history: list[dict] = []

        prev_h = self._qubit.coherence_fraction

        for cycle in range(n_syndrome_cycles):
            # Evolve qubit T1/T2
            self._qubit.step(dt_us)
            self._dm.evolve(dt_us)
            self._p_error = self._qubit.error_rate

            crep = self._crep_calc.compute(self._p_error, t1_us=self._qubit.t1_us)
            # H(t) = 1 - p_error  (per UTAC mapping in class docstring)
            h = 1.0 - self._p_error
            h_star = self._qec.h_star
            dh_dt = (h - prev_h) / dt_us
            prev_h = h

            crep_history.append(crep)
            utac_history.append({"H": h, "dH_dt": dh_dt, "H_star": h_star})

            # Phase event: error-rate coherence H = 1-p drops below H* = 1-p_th
            last_event_far = not self._phase_events or self._phase_events[-1]["cycle"] < cycle - 10
            if h < h_star and last_event_far:
                self._phase_events.append({
                    "cycle": cycle,
                    "type": "decoherence_cascade",
                    "H": round(h, 6),
                    "H_star": round(h_star, 6),
                    "p_error": round(self._p_error, 8),
                    "Gamma": round(crep["Gamma"], 6),
                })

        # Summary
        final_crep = (
            crep_history[-1] if crep_history
            else self._crep_calc.compute(self._p_error, self._qubit.t1_us)
        )
        final_utac = utac_history[-1] if utac_history else {}
        result = {
            "n_syndrome_cycles": n_syndrome_cycles,
            "crep": final_crep,
            "utac": final_utac,
            "phase_events": len(self._phase_events),
            "below_threshold": self._qec.is_below_threshold(self._p_error),
            "p_error_final": round(self._p_error, 8),
            "T1_us_final": round(self._qubit.t1_us, 2),
        }
        self._cycle_results.append(result)
        return result

    def get_crep_state(self) -> dict:
        """Return current CREP tensor {C, R, E, P, Gamma}."""
        return self._crep_calc.compute(self._p_error, self._qubit.t1_us)

    def get_utac_state(self) -> dict:
        """Return current UTAC state {H, dH_dt, H_star, K_eff}."""
        h = 1.0 - self._p_error   # H(t) = 1 - p_error per UTAC mapping
        return {
            "H": round(h, 6),
            "dH_dt": 0.0,                          # instantaneous snapshot
            "H_star": round(self._qec.h_star, 6),
            "K_eff": K_COHERENCE,
            "sigma": SIGMA,
            "r": R_IMPROVEMENT,
        }

    def get_phase_events(self) -> list[dict]:
        """Return list of phase transition events (logical error events)."""
        return list(self._phase_events)

    def to_zenodo_record(self) -> dict:
        """Serialize current state as a Zenodo-compatible metadata dict."""
        crep = self.get_crep_state()
        utac = self.get_utac_state()
        return {
            "title": "QuantumGenesis — Package 24: Qubit Decoherence as UTAC System",
            "description": (
                "Qubit decoherence in superconducting quantum processors modelled "
                "as a UTAC threshold system. The QEC threshold (p_th ≈ 10⁻³) maps "
                "to the UTAC phase transition H*. Calibrated against Google Willow 2024, "
                "IBM Quantum T1 data, and npj Quantum Information 2026."
            ),
            "version": "0.1.0",
            "upload_type": "software",
            "keywords": [
                "quantum decoherence",
                "UTAC",
                "CREP",
                "surface code",
                "QEC threshold",
                "toric code",
                "GenesisAeon",
                "entropy atlas",
                "criticality",
            ],
            "related_identifiers": [
                {
                    "relation": "isDocumentedBy",
                    "identifier": "10.5281/zenodo.19645351",
                    "resource_type": "publication-whitepaper",
                },
                {
                    "relation": "isSupplementTo",
                    "identifier": "10.1007/s10701-025-00883-w",
                    "resource_type": "publication-article",
                },
                {
                    "relation": "isSupplementTo",
                    "identifier": "10.1038/s41534-026-01199-x",
                    "resource_type": "publication-article",
                },
            ],
            "crep_state": crep,
            "utac_state": utac,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # ------------------------------------------------------------------
    # Additional public API
    # ------------------------------------------------------------------

    def is_below_threshold(self) -> bool:
        """True when the system is in the protected QEC regime."""
        return self._qec.is_below_threshold(self._p_error)

    def logical_error_rate(self, code_distance: int = 7) -> float:
        """Logical error rate for given surface code distance."""
        return self._qec.logical_error_rate(self._p_error, code_distance)

    def gamma_quantum(self) -> float:
        """Returns Γ_quantum ≈ 0.050 for calibrated qubit parameters."""
        return self.get_crep_state()["Gamma"]

    def predict_threshold_crossing_probability(
        self,
        horizon_cycles: int = 1000,
    ) -> float:
        """
        UTAC-based probability of crossing H* within horizon_cycles.

        Uses the CREP state as a proxy for proximity to threshold:
        higher Γ → further from threshold → lower crossing probability.
        """
        crep = self.get_crep_state()
        gamma = max(crep["Gamma"], 1e-6)
        # Analytic estimate: P_cross ≈ exp(-γ · horizon / σ)
        return math.exp(-gamma * horizon_cycles / (SIGMA * 100))
