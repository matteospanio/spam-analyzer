import yaml, pytest

import src.cli.run as spam_detector

with open('config.yaml') as f:
    config: dict = yaml.safe_load(f)

@pytest.mark.parametrize("option", ("-h", "--help"))
def test_help(capsys, option):
    try:
        spam_detector.main([option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert config['description'] in output

@pytest.mark.parametrize("option", ("-V", "--version"))
def test_version(capsys, option):
    try:
        spam_detector.main([option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert config['version'] in output
