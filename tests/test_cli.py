import yaml, pytest
import spamdetector.cli.run as spam_detector
from spamdetector import __version__

class TestCLI:

    with open("assets/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    @pytest.mark.parametrize("option", ("-h", "--help"))
    def test_help(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert 'A simple' in output

    @pytest.mark.parametrize("option", ("-V", "--version"))
    def test_version(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert __version__ in output

    @pytest.mark.parametrize("option", ("-v", "--verbose"))
    def test_verbose(self, capsys, option):
        try:
            spam_detector.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert True is False
