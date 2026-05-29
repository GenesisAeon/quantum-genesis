"""Physical and model constants for quantum-genesis (Package 24)."""

from __future__ import annotations

# UTAC parameters
SIGMA: float = 2.2          # CREP coupling constant (universal)
GAMMA_QUANTUM: float = 0.050  # calibrated CREP criticality parameter
K_COHERENCE: float = 1.0    # ceiling: perfect coherence

# QEC threshold (surface code)
P_THRESHOLD: float = 1e-3   # physical error rate threshold (~0.1%)
H_STAR: float = 1.0 - P_THRESHOLD  # UTAC critical point

# Google Willow / IBM Quantum reference values
T1_REFERENCE_US: float = 100.0   # µs T1 energy relaxation (Willow ~100 µs)
T2_MAX_RATIO: float = 2.0         # T2 ≤ 2·T1 (Bloch equations)

# Logical depth factor (Ibnouhsein 2025)
LOGICAL_DEPTH_LD: float = 1.615

# npj 2026: R² for T1 prediction from 14 topological features
R2_T1_GRAPH: float = 0.96

# Information critical phase (Vijay & Lee 2026)
INFO_CRITICAL_FRACTION: float = 0.25  # fractional logical qubit preservation

# Surface code distances (Google Willow benchmarks)
CODE_DISTANCES: list[int] = [3, 5, 7, 9, 11]

# LDPC code threshold (higher than surface code)
P_THRESHOLD_LDPC: float = 2.9e-2

# Coherence improvement rate per hardware generation
R_IMPROVEMENT: float = 0.10

# Default seed for synthetic mode
SEED: int = 42
