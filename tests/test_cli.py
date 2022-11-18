import pytest
import spamdetector.cli.run as spam_detector
from spamdetector import __version__

class TestCLI:
    
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

    @pytest.mark.parametrize("file, option", [("-f tests/samples/invalid_file.txt", "--verbose"), ("-f tests/samples/invalid_file.txt", "-v")])
    def test_verbose_with_not_analyzable_single_file(self, capsys, file, option):
        try:
            spam_detector.main([file, option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert "The file is not analyzable" in output
