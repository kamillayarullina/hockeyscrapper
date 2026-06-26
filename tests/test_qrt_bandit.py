import subprocess
import sys
from pathlib import Path


class TestBanditConfig:
    """QRT-002: Validates bandit security linter configuration and execution."""

    CONFIG_PATH = Path(__file__).parents[1] / "pyproject.toml"

    def test_bandit_config_exists(self):
        content = self.CONFIG_PATH.read_text()
        assert "[tool.bandit]" in content, "pyproject.toml must have [tool.bandit] section"

    def test_bandit_runs_without_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-c", str(self.CONFIG_PATH),
             "-r", "Backend", "services", "-f", "txt"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode in (0, 1), (
            f"bandit exited with unexpected code {result.returncode}: {result.stderr}"
        )

    def test_bandit_completes_in_time(self):
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-c", str(self.CONFIG_PATH),
             "-r", "Backend", "services", "-f", "txt"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode in (0, 1), "bandit timed out or crashed"
