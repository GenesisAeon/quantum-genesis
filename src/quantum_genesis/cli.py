"""CLI for quantum-genesis (Package 24)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="quantum-genesis", help="Package 24 — Qubit Decoherence as UTAC System")
console = Console()


@app.command()
def run(
    t1_us: float = typer.Option(100.0, help="T1 relaxation time [µs]"),
    cycles: int = typer.Option(1000, help="Number of QEC syndrome cycles"),
    seed: int = typer.Option(42, help="RNG seed for synthetic mode"),
) -> None:
    """Run a quantum-genesis UTAC simulation cycle."""
    from .system import QuantumGenesis

    console.print(f"[bold]quantum-genesis[/bold] · Package 24 · T1={t1_us} µs · {cycles} cycles")
    qg = QuantumGenesis(t1_us=t1_us, seed=seed)
    result = qg.run_cycle(n_syndrome_cycles=cycles)

    crep = result["crep"]
    utac = result["utac"]

    table = Table(title="CREP State")
    table.add_column("Component", style="cyan")
    table.add_column("Value", justify="right")
    for k, v in crep.items():
        table.add_row(k, f"{v:.6f}")
    console.print(table)

    console.print(f"H = {utac.get('H', '?'):.4f}  H* = {utac.get('H_star', '?'):.4f}")
    console.print(f"Below threshold: {result['below_threshold']}")
    console.print(f"Phase events: {result['phase_events']}")


@app.command()
def benchmark() -> None:
    """Run benchmark against literature targets."""
    from .benchmark import print_benchmark_report, run_benchmark

    results = run_benchmark()
    print_benchmark_report(results)


@app.command()
def info() -> None:
    """Show package information and CREP criticality context."""
    from . import GAMMA_QUANTUM, __package_id__, __version__

    console.print(f"[bold]quantum-genesis[/bold] v{__version__}")
    console.print(f"Package ID : {__package_id__}")
    label = f"Γ_quantum  : {GAMMA_QUANTUM:.3f}  (most fragile UTAC system after solar flares)"
    console.print(label)
    console.print("DOI        : 10.5281/zenodo.19645351")
