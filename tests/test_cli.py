import toml, pytest
import spamdetector.cli.run as spam_detector

class TestCLI:

    config = toml.load('pyproject.toml')
    
    @pytest.mark.parametrize("option", ("-h", "--help"))
    def test_help(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert self.config['project']['description'] in output

    @pytest.mark.parametrize("option", ("-V", "--version"))
    def test_version(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert self.config['version'] in output

    @pytest.mark.parametrize("option", ("-v", "--verbose"))
    def test_verbose(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert True is False