import tomli
from click.testing import CliRunner

from app import __main__
from app.__analyzer import analyze


class TestCLI:
    runner = CliRunner()
    cli = __main__.cli
    cli.add_command(analyze)

    def test_help(self):
        result = self.runner.invoke(self.cli, ["--help"])
        assert result.exit_code == 0
        assert "A simple" in result.output
        assert "Usage" in result.output

    def test_version(self):
        result = self.runner.invoke(self.cli, ["--version"])
        output = result.output
        with open("pyproject.toml", "rb") as f:
            config = tomli.load(f)
            assert config["tool"]["poetry"]["version"] in output

    def test_verbose_with_not_analyzable_single_file(self):
        result = self.runner.invoke(
            self.cli,
            [
                "-v",
                "analyze",
                "-l",
                "src/app/conf/word_blacklist.txt",
                "tests/samples/invalid_file.txt",
            ],
        )
        assert "The file is not analyzable" in result.output
        assert result.exit_code == 1

    def test_integration_single_email(self):
        result = self.runner.invoke(
            self.cli,
            [
                "analyze",
                "-l",
                "src/app/conf/word_blacklist.txt",
                "tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email",
            ],
        )
        output = result.output
        assert result.exit_code == 0
        assert "Summary" in output
        assert "SPAM" in output

    def test_integration_folder(self):
        result = self.runner.invoke(
            self.cli,
            [
                "analyze",
                "-l",
                "src/app/conf/word_blacklist.txt",
                "tests/samples",
            ],
        )
        assert 0 == result.exit_code
