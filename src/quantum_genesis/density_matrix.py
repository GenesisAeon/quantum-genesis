"""Density matrix coherence tracker for a single qubit."""

from __future__ import annotations

import math


class DensityMatrixCoherence:
    """
    Tracks the 2×2 density matrix ρ of a qubit under Lindblad dynamics.

    ρ = [[ρ_00, ρ_01],
         [ρ_10, ρ_11]]

    Diagonal: populations.  Off-diagonal: coherences.
    C-component of CREP = |ρ_01| (off-diagonal magnitude, ∈ [0, 0.5]).
    """

    def __init__(self, t1_us: float, t2_us: float) -> None:
        self.t1_us = t1_us
        self.t2_us = t2_us
        # Start in |+⟩ = equal superposition
        self.rho_00: float = 0.5
        self.rho_11: float = 0.5
        self.rho_01: complex = complex(0.5, 0.0)  # off-diagonal coherence

    # ------------------------------------------------------------------
    def evolve(self, dt_us: float) -> None:
        """Lindblad evolution: T1 decay + T2 dephasing."""
        gamma1 = 1.0 / self.t1_us
        gamma2 = 1.0 / self.t2_us

        # Population decay
        decay1 = math.exp(-gamma1 * dt_us)
        self.rho_11 *= decay1
        self.rho_00 = 1.0 - self.rho_11

        # Coherence decay (T2 ≤ T1/2 + T_phi)
        decay2 = math.exp(-gamma2 * dt_us)
        self.rho_01 *= decay2

    @property
    def coherence(self) -> float:
        """Off-diagonal coherence |ρ_01| normalised to [0, 1]."""
        return min(abs(self.rho_01) * 2.0, 1.0)

    @property
    def purity(self) -> float:
        """Tr(ρ²) — 1.0 for pure state, 0.5 for fully mixed."""
        return self.rho_00**2 + self.rho_11**2 + 2 * abs(self.rho_01) ** 2

    def reset_superposition(self) -> None:
        self.rho_00 = 0.5
        self.rho_11 = 0.5
        self.rho_01 = complex(0.5, 0.0)
