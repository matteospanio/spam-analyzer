import pytest
import app.__main__ as __main__
import tomli
from app import files

from click.testing import CliRunner


_, _, _ = files.handle_configuration_files()


class TestCLI:
    runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(__main__.cli, ["--help"])
        assert result.exit_code == 0
        assert "A simple" in result.output
        assert "Usage" in result.output

    def test_version(self):
        result = self.runner.invoke(__main__.cli, ["--version"])
        output = result.output
        with open("pyproject.toml", "rb") as f:
            config = tomli.load(f)
            assert config["tool"]["poetry"]["version"] in output

    def test_verbose_with_not_analyzable_single_file(self):
        result = self.runner.invoke(
            __main__.cli, ["-v", "analyze", "tests/samples/invalid_file.txt"]
        )
        output = result.output
        assert "The file is not analyzable" in output
