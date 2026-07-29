"""CLI for quantum-genesis (Package 24)."""

from __future__ import annotations

import io
import sys

import typer
from rich.console import Console
from rich.table import Table

# Windows consoles default to a non-UTF-8 codepage, which breaks the Greek
# letters and micro symbol used throughout this CLI with
# UnicodeEncodeError. Force UTF-8 stdout/stderr so behavior matches
# Linux/macOS terminals.
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

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

    console.print(
        f"[bold]quantum-genesis[/bold] - Package 24 - T1={t1_us} us - {cycles} cycles",
        highlight=False,
    )
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

    console.print(
        f"H = {utac.get('H', '?'):.4f}  H* = {utac.get('H_star', '?'):.4f}", highlight=False
    )
    console.print(f"Below threshold: {result['below_threshold']}", highlight=False)
    console.print(f"Phase events: {result['phase_events']}", highlight=False)


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

    console.print(f"[bold]quantum-genesis[/bold] v{__version__}", highlight=False)
    console.print(f"Package ID : {__package_id__}", highlight=False)
    label = f"Gamma_quantum  : {GAMMA_QUANTUM:.3f}  (most fragile UTAC system after solar flares)"
    console.print(label, highlight=False)
    console.print("DOI        : 10.5281/zenodo.19645351", highlight=False)


if __name__ == "__main__":
    app()
