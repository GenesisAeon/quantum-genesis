"""Toric code information critical phase (Vijay & Lee 2026)."""

from __future__ import annotations

import random

from .constants import INFO_CRITICAL_FRACTION, P_THRESHOLD, SEED


class InformationCriticalPhase:
    """
    Information critical phase from Vijay & Lee (2026).

    In decohered Toric codes, an extended region exists where:
    - Neither full protection nor complete loss of logical information.
    - Coherent information saturates to fractional value f ∈ (0, 1).
    - Markov length diverges (critical slowing down signature).

    This IS the UTAC critical fixed point for the quantum domain.
    Maps Markov length divergence to CREP C-component (coherence).
    """

    # Boundaries of the information critical phase
    P_LOWER: float = P_THRESHOLD * 0.5   # ~5 × 10⁻⁴
    P_UPPER: float = P_THRESHOLD * 2.0   # ~2 × 10⁻³

    def __init__(self, seed: int = SEED) -> None:
        self._rng = random.Random(seed)
        self.target_fraction = INFO_CRITICAL_FRACTION

    # ------------------------------------------------------------------
    def coherent_information(self, p: float) -> float:
        """
        Coherent information I_c as function of physical error rate p.

        Below p_lower: I_c ≈ 1.0 (full protection).
        In critical phase: I_c ≈ f (fractional preservation, ~0.25).
        Above p_upper: I_c ≈ 0.0 (complete loss).
        """
        if p < self.P_LOWER:
            return 1.0 + self._rng.gauss(0, 0.01)
        if p > self.P_UPPER:
            return max(0.0, self._rng.gauss(0, 0.02))
        # Critical phase: fractional preservation with noise
        return self.target_fraction + self._rng.gauss(0, 0.05)

    def markov_length(self, p: float) -> float:
        """
        Markov length ξ — diverges at critical boundaries.

        ξ ∝ |p - p_c|^(-ν)  with ν ≈ 1.0 (correlation length exponent).
        """
        p_c = (self.P_LOWER + self.P_UPPER) / 2.0
        distance = abs(p - p_c)
        if distance < 1e-6:
            return 1e6   # numerical infinity
        return 1.0 / distance

    def is_in_critical_phase(self, p: float) -> bool:
        return self.P_LOWER <= p <= self.P_UPPER

    def crep_coherence(self, p: float) -> float:
        """
        CREP C-component from Markov length (normalised).

        High ξ → high C (long-range coherence signature).
        """
        xi = self.markov_length(p)
        xi_ref = 1.0 / (self.P_UPPER - self.P_LOWER)  # scale
        return min(xi / (xi + xi_ref), 1.0)
