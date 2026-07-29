"""Tests for the quantum-genesis CLI commands (run / benchmark / info).

Note: this file previously contained an unmodified copy of diamond-setup's
own test_cli.py (testing diamond_setup.cli's scaffold/validate/version
commands) -- a scaffold leftover never adapted to this package. It gave a
false impression of CLI test coverage while quantum-genesis's own CLI had
none at all, which is also why the __version__ drift (see
quantum_genesis/__init__.py) went uncaught: the old test_version() asserted
against diamond_setup.__version__, not this package's.
"""

from __future__ import annotations

from typer.testing import CliRunner

from quantum_genesis import __version__
from quantum_genesis.cli import app

runner = CliRunner()


def test_info_shows_own_version():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert __version__ in result.output
    assert "Package ID : 24" in result.output


def test_run_default():
    result = runner.invoke(app, ["run", "--cycles", "10"])
    assert result.exit_code == 0, result.output
    assert "CREP State" in result.output
    assert "Below threshold" in result.output


def test_run_custom_t1():
    result = runner.invoke(app, ["run", "--t1-us", "50.0", "--cycles", "10"])
    assert result.exit_code == 0, result.output
    assert "T1=50.0" in result.output


def test_benchmark_all_pass():
    result = runner.invoke(app, ["benchmark"])
    assert result.exit_code == 0, result.output
    assert "Overall: ALL PASS" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "benchmark" in result.output
    assert "info" in result.output
