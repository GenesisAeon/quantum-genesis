"""Logical depth factor L_d from Ibnouhsein 2025 (Foundations of Physics 55, 71)."""

from __future__ import annotations

import math

from .constants import LOGICAL_DEPTH_LD


def logical_depth_factor(conditional: bool = True) -> float:
    """
    Thermodynamic logical depth L_d for quantum circuits.

    L_d ≈ 1.615 for conditional (adaptive) vs. uniform architectures.
    Reference: Ibnouhsein 2025 — DOI: 10.1007/s10701-025-00883-w

    Interpretation: conditional circuits extract ~61.5% more useful
    thermodynamic work than non-adaptive ones for the same physical depth,
    quantifying the computational advantage of feed-forward operations.
    """
    return LOGICAL_DEPTH_LD if conditional else 1.0


def entropy_cost(n_qubits: int, depth: int, p_error: float, conditional: bool = True) -> float:
    """
    Thermodynamic entropy cost of a quantum circuit (arbitrary units).

    S_cost = n_qubits · depth · p_error / L_d

    Lower S_cost means more thermodynamically efficient computation.
    Conditional circuits reduce entropy cost by factor L_d.
    """
    ld = logical_depth_factor(conditional)
    return (n_qubits * depth * p_error) / ld


def crep_p_from_logical_depth(p_error: float, n_qubits: int = 50, depth: int = 100) -> float:
    """
    CREP P-component (Poetics/complexity) derived from logical depth entropy.

    Low entropy cost → high P (rich computational structure).
    P = 1 - S_cost_normalised, clipped to [0, 1].
    """
    s = entropy_cost(n_qubits, depth, p_error, conditional=True)
    s_max = entropy_cost(n_qubits, depth, 1.0, conditional=False)
    if s_max == 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - s / s_max))
