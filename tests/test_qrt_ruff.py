import subprocess
import sys
from pathlib import Path


class TestRuffConfig:
    """QRT-004: Validates ruff linter configuration and execution."""

    CONFIG_PATH = Path(__file__).parents[1] / "pyproject.toml"

    def test_ruff_config_exists(self):
        content = self.CONFIG_PATH.read_text()
        assert "[tool.ruff]" in content, "pyproject.toml must have [tool.ruff] section"

    def test_ruff_check_passes(self):
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            capture_output=True, text=True, timeout=60,
            cwd=Path(__file__).parents[1],
        )
        assert result.returncode == 0, (
            f"ruff check failed with code {result.returncode}:\n{result.stdout}\n{result.stderr}"
        )
