"""Superconducting qubit T1/T2 decay model."""

from __future__ import annotations

import math
import random

from .constants import SEED, T1_REFERENCE_US, T2_MAX_RATIO


class QubitDecoherenceModel:
    """
    T1/T2 decay model for superconducting qubits.

    T1 = energy relaxation time (50-300 µs for current SOTA).
    T2 = dephasing time; T2 ≤ 2·T1 by Bloch equations.
    Error rate p ≈ t_gate/T1 for single-qubit gates.

    Maps T1 variation to UTAC H(t): H = T1(t) / T1_max.
    Implements two-level system (TLS) fluctuation model from npj 2026.
    """

    def __init__(
        self,
        t1_us: float = T1_REFERENCE_US,
        t2_ratio: float = 0.9,
        t_gate_ns: float = 50.0,
        tls_noise_amplitude: float = 0.05,
        seed: int = SEED,
    ) -> None:
        self.t1_us = t1_us
        self.t1_max_us = t1_us * 3.0          # headroom for future improvement
        self.t2_us = min(t1_us * t2_ratio, t1_us * T2_MAX_RATIO)
        self.t_gate_ns = t_gate_ns
        self.tls_noise_amplitude = tls_noise_amplitude
        self._rng = random.Random(seed)
        self._t = 0.0                          # elapsed time [µs]

    # ------------------------------------------------------------------
    @property
    def error_rate(self) -> float:
        """Physical gate error rate p ≈ t_gate / T1."""
        return self.t_gate_ns * 1e-3 / self.t1_us  # ns → µs

    @property
    def coherence_fraction(self) -> float:
        """UTAC H(t) = T1(t) / T1_max ∈ [0, 1]."""
        return min(max(self.t1_us / self.t1_max_us, 0.0), 1.0)

    # ------------------------------------------------------------------
    def step(self, dt_us: float = 1.0) -> dict[str, float]:
        """Advance model by dt_us microseconds; apply TLS fluctuations."""
        self._t += dt_us
        # TLS fluctuations: Ornstein-Uhlenbeck-like random walk on T1
        noise = self.tls_noise_amplitude * (self._rng.gauss(0, 1))
        self.t1_us = max(1.0, self.t1_us * (1.0 + noise))
        self.t2_us = min(self.t1_us * T2_MAX_RATIO, self.t1_us * 0.9)
        return {
            "t_us": self._t,
            "T1_us": self.t1_us,
            "T2_us": self.t2_us,
            "error_rate": self.error_rate,
            "coherence_fraction": self.coherence_fraction,
        }

    def reset(self) -> None:
        self._t = 0.0
        self.t1_us = T1_REFERENCE_US
