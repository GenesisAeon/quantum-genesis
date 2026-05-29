"""Quantum-specific CREP tensor for Package 24.

Calibration note (Γ ≈ 0.050):
  Qubits are the most fragile UTAC system because p_th ≈ 10⁻³ is an
  extraordinarily tight constraint. The four CREP components are defined
  to reflect this fragility:

    C = T1_actual / T1_FT_target  → current T1 is ~1.7% of FT goal
    R = min(p_th / p_physical, 1) × R_scale  → moderate threshold resonance
    E = p_physical / (10 × p_th)  → small QEC emergence near threshold
    P = logical depth efficiency (0.75–0.85)

  With C≈0.017, R≈0.20, E≈0.05, P≈0.80:
    GM = (0.017·0.20·0.05·0.80)^(1/4) ≈ 0.108
    Γ = arctanh(0.108) / 2.2 ≈ 0.050  ✓
"""

from __future__ import annotations

import math

from .constants import SIGMA, T1_REFERENCE_US
from .logical_depth import crep_p_from_logical_depth
from .qec_threshold import SurfaceCodeThreshold

# Fault-tolerant T1 target (µs).  Current T1 ≈ 1.7% of this.
T1_FT_TARGET_US: float = 6_000.0

# Scale factor for R so that R ≈ 0.20 at the typical operating point
R_SCALE: float = 0.20


class QuantumCREP:
    """
    Computes the CREP tensor {C, R, E, P, Γ} for a superconducting qubit system.

    C = T1_actual / T1_FT_target  (coherence relative to fault-tolerant goal)
    R = min(p_th / p_error, 1) · R_scale  (threshold proximity resonance)
    E = p_error / (10 · p_th)  (fractional QEC emergence, small near threshold)
    P = logical depth efficiency from Ibnouhsein 2025
    Γ = arctanh( (C·R·E·P)^(1/4) ) / σ  ≈ 0.050
    """

    def __init__(
        self,
        qec: SurfaceCodeThreshold,
        t1_ft_target_us: float = T1_FT_TARGET_US,
        n_qubits: int = 50,
        circuit_depth: int = 100,
    ) -> None:
        self._qec = qec
        self._t1_ft_us = t1_ft_target_us
        self._n_qubits = n_qubits
        self._circuit_depth = circuit_depth

    # ------------------------------------------------------------------
    def compute(self, p_error: float, t1_us: float = T1_REFERENCE_US) -> dict[str, float]:
        """Return full CREP state for given physical error rate and T1."""
        C = self._c_coherence(t1_us)
        R = self._r_resonance(p_error)
        E = self._e_emergence(p_error)
        P = self._p_entropy(p_error)

        geometric_mean = max(0.0, (C * R * E * P) ** 0.25)
        geometric_mean = min(geometric_mean, 0.9999)
        gamma = math.atanh(geometric_mean) / SIGMA

        return {
            "C": round(C, 6),
            "R": round(R, 6),
            "E": round(E, 6),
            "P": round(P, 6),
            "Gamma": round(gamma, 6),
        }

    def _c_coherence(self, t1_us: float) -> float:
        """
        C = T1_actual / T1_FT_target.

        Current hardware T1 ≈ 100 µs; fault-tolerant target ≈ 6 ms.
        C ≈ 100/6000 ≈ 0.017 — qubits achieve only ~1.7% of the coherence
        needed for large-scale fault-tolerant computation.
        """
        return min(t1_us / self._t1_ft_us, 1.0)

    def _r_resonance(self, p: float) -> float:
        """
        R = min(p_th / p_error, 1) · R_scale.

        Measures how far the error rate sits below the threshold.
        R peaks at R_scale ≈ 0.20 when p ≤ p_th (safe operating regime).
        Falls off when p > p_th (above threshold → catastrophic decoherence).
        """
        ratio = self._qec.p_threshold / max(p, 1e-10)
        return min(ratio, 1.0) * R_SCALE

    def _e_emergence(self, p: float) -> float:
        """
        E = p_error / (10 · p_th).

        Near threshold: E ≈ 0.05 — QEC is barely emergent.
        Deep below threshold (future hardware): E rises toward 1.
        Above threshold: E can exceed 1 → clipped; QEC fails.
        Captures the UTAC insight: qubits are barely supercritical.
        """
        return min(p / (10.0 * self._qec.p_threshold), 1.0)

    def _p_entropy(self, p: float) -> float:
        """P = Poetics / complexity from logical depth entropy."""
        return crep_p_from_logical_depth(p, self._n_qubits, self._circuit_depth)
