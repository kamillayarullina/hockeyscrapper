import configparser
from pathlib import Path


class TestCoverageConfig:
    """QRT-001: Validates coverage configuration exists and enforces threshold."""

    CONFIG_PATH = Path(__file__).parents[1] / ".coveragerc"

    def test_coveragerc_exists(self):
        assert self.CONFIG_PATH.exists(), ".coveragerc file must exist to enforce coverage gate"

    def test_fail_under_threshold(self):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_PATH)
        fail_under = config.getint("report", "fail_under", fallback=None)
        assert fail_under is not None, ".coveragerc must have [report] fail_under set"
        assert fail_under >= 20, f"fail_under must be >= 20, got {fail_under}"

    def test_source_modules_configured(self):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_PATH)
        source = config.get("run", "source", fallback="")
        modules = [m.strip() for m in source.split(",") if m.strip()]
        assert "Backend" in modules, "Backend must be in [run] source"
        assert "services" in modules, "services must be in [run] source"
