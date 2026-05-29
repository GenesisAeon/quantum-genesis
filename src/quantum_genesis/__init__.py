"""
quantum-genesis — Package 24: Qubit Decoherence as UTAC Threshold System.

GenesisAeon Entropy Atlas · Johann Römer · MOR Research Collective · 2026

References:
  Ibnouhsein 2025  — DOI: 10.1007/s10701-025-00883-w
  npj QI 2026      — DOI: 10.1038/s41534-026-01199-x
  Google Willow 2024 / Vijay & Lee 2026
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Johann Römer / MOR Research Collective"
__package_id__ = 24

from .benchmark import QUANTUM_TARGETS, run_benchmark
from .constants import GAMMA_QUANTUM, P_THRESHOLD, SIGMA
from .system import QuantumGenesis

__all__ = [
    "QuantumGenesis",
    "GAMMA_QUANTUM",
    "P_THRESHOLD",
    "SIGMA",
    "QUANTUM_TARGETS",
    "run_benchmark",
]
