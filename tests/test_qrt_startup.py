import importlib
import subprocess
import sys
from pathlib import Path


class TestStartupReliability:
    """QRT-005: Validates application startup integrity."""

    PROJECT_ROOT = Path(__file__).parents[1]

    def test_main_module_imports(self):
        import main as main_module
        assert hasattr(main_module, "main"), "main.py must expose main()"
        assert hasattr(main_module, "load_env"), "main.py must expose load_env()"
        assert hasattr(main_module, "run_api"), "main.py must expose run_api()"

    def test_core_modules_import(self):
        modules = [
            "Backend.main",
            "bot.telegram_bot",
            "services.database",
            "services.notifier",
            "services.parser_runner",
            "services.team_matcher",
            "parsers.base_parser",
            "parsers.protection_detector",
        ]
        for mod_name in modules:
            mod = importlib.import_module(mod_name)
            assert mod is not None, f"Failed to import {mod_name}"

    def test_cli_parser_responds(self):
        result = subprocess.run(
            [sys.executable, str(self.PROJECT_ROOT / "main.py"), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, f"CLI parser failed: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower()

    def test_load_env_without_dotenv(self):
        from importlib import reload
        import main
        env_path = self.PROJECT_ROOT / ".env"
        if env_path.exists():
            renamed = False
            tmp_path = env_path.with_suffix(".env.bak")
            env_path.rename(tmp_path)
            renamed = True
        else:
            renamed = False
        try:
            reload(main)
            main.load_env()
        finally:
            if renamed:
                tmp_path.rename(env_path)
