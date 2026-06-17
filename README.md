# quantum-genesis

[![Package 24](https://img.shields.io/badge/GenesisAeon-Package%2024-blueviolet)](https://github.com/GenesisAeon/quantum-genesis)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-10.5281%2Fzenodo.19645351-blue)](https://doi.org/10.5281/zenodo.19645351)
[![PyPI](https://img.shields.io/pypi/v/quantum-genesis)](https://pypi.org/project/quantum-genesis/)
[![CI](https://github.com/GenesisAeon/quantum-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/quantum-genesis/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zenodo](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.19645351-lightgrey)](https://doi.org/10.5281/zenodo.19645351)

**Qubit decoherence as a UTAC threshold system** — Package 24 of the GenesisAeon Entropy Atlas.

Models superconducting qubit decoherence via the **CREP** (Coherence–Resonance–Emergence–Poetics) framework, coupling the QEC threshold theorem to the Unified Threshold Adaptive Criticality (UTAC) system.

> **Central result:** Γ_quantum ≈ 0.050 — qubits are the most fragile UTAC system in the Entropy Atlas (just above solar magnetic flares at Γ ≈ 0.014). This quantifies why quantum computing is extraordinarily difficult: any perturbation can cross the phase boundary.

---

## CREP Criticality Spectrum — quantum-genesis in context

| Domain | Package | Γ | Note |
|--------|---------|---|------|
| Solar flare magnetic field | P21 | 0.014 | Ultra-sensitive |
| Cygnus X-1 jet | P17 | 0.046 | Hair-trigger |
| **Qubit decoherence (T2)** | **P24** | **0.050** | **← quantum-genesis** |
| Apoptosis ATP threshold | P25 | 0.090 | Cellular critical |
| Amazon rainforest | P19 | 0.116 | Ecological fragile |
| Neural criticality / AMOC | P18/P20 | 0.251 | Homeostatic universal |

---

## Physical Mapping to UTAC

```
H(t)  ← coherence fraction = (1 − p_error) ∈ [0, 1]
K     ← 1.0   (perfect coherence ceiling)
H*    ← 1 − p_threshold ≈ 0.999   (QEC phase boundary)
r     ← 0.10  (coherence improvement rate per generation)
σ     ← 2.2   (universal CREP coupling)
```

**CREP tensor components:**

| Symbol | Meaning |
|--------|---------|
| C | Off-diagonal density matrix coherence \|ρ₀₁\| |
| R | Proximity of error rate to QEC threshold (resonance at p_th) |
| E | Logical vs. physical error rate ratio (emergent QEC benefit) |
| P | Entropy of T1 distribution / logical depth efficiency |

**Phase transition:** The QEC threshold at p_th ≈ 10⁻³ is the UTAC phase boundary.
Below threshold → stable logical qubit. Above threshold → decoherence cascade.
At threshold → information critical phase (Vijay & Lee 2026): fractional logical qubit preservation f ≈ 0.25.

---

## Installation

```bash
pip install quantum-genesis
# or
uv add quantum-genesis

# Optional backends
pip install quantum-genesis[sim]   # stim + qiskit-ibm-runtime
```

## Quickstart

```python
from quantum_genesis import QuantumGenesis

qg = QuantumGenesis(t1_us=100.0)       # Google Willow reference T1

# Run 1000 QEC syndrome cycles
result = qg.run_cycle(n_syndrome_cycles=1000)
print(result)
# {'n_syndrome_cycles': 1000, 'crep': {'C': ..., 'R': ..., 'E': ..., 'P': ..., 'Gamma': 0.049...}, ...}

# Diamond interface
print(qg.get_crep_state())   # {C, R, E, P, Gamma}
print(qg.get_utac_state())   # {H, dH_dt, H_star, K_eff}
print(qg.get_phase_events()) # decoherence cascade events
print(qg.is_below_threshold())        # True
print(qg.logical_error_rate(d=7))     # surface code d=7
print(qg.gamma_quantum())             # ≈ 0.050

# Zenodo metadata record
record = qg.to_zenodo_record()
```

## Diamond Interface Contract

All GenesisAeon packages implement this interface:

```python
class QuantumGenesis:
    def run_cycle(self, n_syndrome_cycles: int = 1000) -> dict: ...
    def get_crep_state(self) -> dict:    # {C, R, E, P, Gamma}
    def get_utac_state(self) -> dict:    # {H, dH_dt, H_star, K_eff}
    def get_phase_events(self) -> list:  # logical error events
    def to_zenodo_record(self) -> dict:  # Zenodo-compatible metadata
```

## Benchmark Targets

| Metric | Target | Tolerance | Source |
|--------|--------|-----------|--------|
| QEC threshold [%] | 0.100 | ±0.03 | Surface code theory |
| Google Willow T1 [µs] | 100.0 | ±30% | Willow 2024 |
| Logical depth L_d | 1.615 | ±0.05 | Ibnouhsein 2025 |
| R² (T1 from topology) | 0.96 | ±0.02 | npj QI 2026 |
| **Γ_quantum** | **0.050** | **±0.010** | CREP calibration |
| Info. critical fraction | 0.25 | ±0.10 | Vijay & Lee 2026 |

Run benchmarks:

```python
from quantum_genesis.benchmark import run_benchmark, print_benchmark_report
results = run_benchmark()
print_benchmark_report(results)
```

## Repository Structure

```
quantum-genesis/
├── src/quantum_genesis/
│   ├── system.py             # QuantumGenesis — Diamond interface
│   ├── qubit_model.py        # T1/T2 decay + TLS fluctuation model
│   ├── density_matrix.py     # Lindblad density matrix evolution
│   ├── qec_threshold.py      # Surface code threshold analysis
│   ├── toric_code.py         # Information critical phase (Vijay & Lee 2026)
│   ├── topology_features.py  # 14 graph features → T1 prediction (npj 2026)
│   ├── crep_quantum.py       # Quantum CREP tensor
│   ├── logical_depth.py      # Logical depth L_d (Ibnouhsein 2025)
│   ├── stim_interface.py     # stim surface code simulator (optional)
│   ├── benchmark.py          # Literature benchmark targets
│   └── constants.py
├── notebooks/
│   ├── 01_qubit_utac_overview.ipynb
│   ├── 02_qec_threshold_phase_transition.ipynb
│   ├── 03_information_critical_phase.ipynb
│   ├── 04_logical_depth_entropy.ipynb
│   └── 05_gamma_quantum_calibration.ipynb
├── data/
│   ├── ibm_quantum_t1_public.yaml
│   └── willow_2024_targets.yaml
└── src/diamond_setup/          # scaffold tool (diamond-setup v1.0.0)
```

## References

- **Ibnouhsein 2025** — Thermodynamic signature of logical depth in quantum circuits.
  *Foundations of Physics* 55, 71. [DOI: 10.1007/s10701-025-00883-w](https://doi.org/10.1007/s10701-025-00883-w)

- **npj Quantum Information 2026** — Machine learning decoherence from graph connectivity.
  [DOI: 10.1038/s41534-026-01199-x](https://doi.org/10.1038/s41534-026-01199-x)
  R² > 0.96 for T1 prediction from 14 topological features.

- **Vijay & Lee 2026** — Decoherence enables information critical phases.
  Fractional topological memory in decohered Toric codes.

- **Google Willow 2024** — Below-threshold QEC demonstrated.
  Logical error rate decreases exponentially with code distance.

- **GenesisAeon Whitepaper** — [DOI: 10.5281/zenodo.19645351](https://doi.org/10.5281/zenodo.19645351)

## Falsifiable Prediction

> As T1 improves toward 1 ms (next-generation qubits), Γ_quantum will increase from 0.050 toward 0.100, placing quantum systems in the "cellular critical" range — equivalent to the apoptosis ATP threshold (Package 25). Testable against IBM Quantum roadmap milestones (public).

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PLACEHOLDER.svg)](https://doi.org/10.5281/zenodo.PLACEHOLDER)

DOI will be assigned automatically on first GitHub Release once
Zenodo–GitHub integration is enabled for this repo. (The whitepaper DOI
below, `10.5281/zenodo.19645351`, already exists and documents the
package's scientific model; the software-specific DOI is separate and
versioned per release.)

```bibtex
@software{romer_quantum_genesis_2026,
  author    = {Römer, Johann and MOR Research Collective},
  title     = {quantum-genesis: Qubit Decoherence as UTAC Threshold System},
  year      = {2026},
  publisher = {Zenodo},
  version   = {0.1.0},
  doi       = {10.5281/zenodo.19645351},
  url       = {https://doi.org/10.5281/zenodo.19645351}
}
```

---

*GenesisAeon Entropy Atlas · Package 24 of 30 · Johann Römer · MOR Research Collective · 2026*
