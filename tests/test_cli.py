import pytest
import spamanalyzer.cli.run as spam_analyzer
import spamanalyzer.files as files
from spamanalyzer import __version__

_, _, _ = files.handle_configuration_files()

class TestCLI:
    
    @pytest.mark.parametrize("option", ("-h", "--help"))
    def test_help(self, capsys, option):
        try:
            spam_analyzer.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert 'A simple' in output

    @pytest.mark.parametrize("option", ("-V", "--version"))
    def test_version(self, capsys, option):
        try:
            spam_analyzer.main([option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert __version__ in output

    @pytest.mark.parametrize("file, option", [("-f tests/samples/invalid_file.txt", "--verbose"), ("-f tests/samples/invalid_file.txt", "-v")])
    def test_verbose_with_not_analyzable_single_file(self, capsys, file, option):
        try:
            spam_analyzer.main([file, option])
        except SystemExit:
            pass
        output = capsys.readouterr().out
        assert "The file is not analyzable" in output
