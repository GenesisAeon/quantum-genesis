"""Interface to stim surface code simulator (optional dependency)."""

from __future__ import annotations

import warnings

from .constants import CODE_DISTANCES, P_THRESHOLD, SEED


class StimInterface:
    """
    Thin wrapper around stim for surface code Monte Carlo simulation.

    Falls back gracefully to analytic approximation when stim is not installed.
    Install with: pip install stim
    """

    def __init__(self, seed: int = SEED) -> None:
        self.seed = seed
        self._stim_available = self._check_stim()

    @staticmethod
    def _check_stim() -> bool:
        try:
            import stim  # noqa: F401
            return True
        except ImportError:
            return False

    def sample_logical_error_rate(
        self,
        p: float,
        d: int = 5,
        n_shots: int = 10_000,
    ) -> float:
        """
        Monte Carlo logical error rate for surface code at distance d.

        Uses stim if available; otherwise returns analytic approximation.
        """
        if self._stim_available:
            return self._stim_sample(p, d, n_shots)
        warnings.warn(
            "stim not installed — using analytic approximation. "
            "Install with: pip install stim",
            stacklevel=2,
        )
        return self._analytic_fallback(p, d)

    def _stim_sample(self, p: float, d: int, n_shots: int) -> float:
        import stim

        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d,
            distance=d,
            after_clifford_depolarization=p,
            before_measure_flip_probability=p,
            after_reset_flip_probability=p,
        )
        sampler = circuit.compile_detector_sampler(seed=self.seed)
        det_data, obs_data = sampler.sample(n_shots, separate_observables=True)
        n_errors = int(obs_data.sum())
        return n_errors / n_shots

    @staticmethod
    def _analytic_fallback(p: float, d: int) -> float:
        """Fowler et al. 2012 analytic approximation."""
        ratio = p / P_THRESHOLD
        exponent = (d + 1) / 2
        return min(1.0, 0.1 * ratio**exponent)

    @property
    def backend(self) -> str:
        return "stim" if self._stim_available else "analytic"
