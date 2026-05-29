"""Surface code QEC threshold analysis."""

from __future__ import annotations

import math
import random

from .constants import CODE_DISTANCES, P_THRESHOLD, SEED


class SurfaceCodeThreshold:
    """
    Surface code QEC threshold analysis.

    Physical error rate p vs. logical error rate p_L(p, d) for code distance d.
    Threshold at p_th ≈ 10⁻³ (surface code).

    Below threshold: p_L decreases exponentially with d.
    Above threshold: p_L increases — runaway decoherence cascade.

    Maps to UTAC phase transition: H* = 1 - p_th.
    Uses analytic approximation (no stim required) in synthetic mode.
    """

    def __init__(
        self,
        p_threshold: float = P_THRESHOLD,
        code_distances: list[int] | None = None,
        seed: int = SEED,
    ) -> None:
        self.p_threshold = p_threshold
        self.distances = code_distances or CODE_DISTANCES
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    def logical_error_rate(self, p: float, d: int) -> float:
        """
        Analytic surface code logical error rate (Fowler et al. 2012 approx).

        p_L ≈ A · (p / p_th)^((d+1)/2)  for p near p_th.
        """
        if p <= 0.0:
            return 0.0
        ratio = p / self.p_threshold
        exponent = (d + 1) / 2
        # prefactor A ≈ 0.1 (fitted to Monte Carlo data)
        A = 0.1
        p_L = A * ratio**exponent
        # Add small shot noise for realism
        p_L *= 1.0 + self._rng.gauss(0, 0.02)
        return max(0.0, min(1.0, p_L))

    def is_below_threshold(self, p: float) -> bool:
        return p < self.p_threshold

    def qec_gain(self, p: float, d: int = 7) -> float:
        """Ratio p / p_L — how much QEC improves error rate."""
        p_L = self.logical_error_rate(p, d)
        if p_L == 0.0:
            return float("inf")
        return p / p_L

    def threshold_scan(self, p_values: list[float] | None = None) -> list[dict]:
        """Scan logical error rate across physical error rates for all distances."""
        if p_values is None:
            p_values = [10 ** (-k / 2) for k in range(2, 8)]
        return [
            {
                "p_physical": p,
                "d": d,
                "p_logical": self.logical_error_rate(p, d),
                "below_threshold": self.is_below_threshold(p),
            }
            for p in p_values
            for d in self.distances
        ]

    @property
    def h_star(self) -> float:
        """UTAC critical coherence fraction H* = 1 - p_threshold."""
        return 1.0 - self.p_threshold
