import yaml, pytest, importlib

spam_detector = importlib.import_module('spam-detector')

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
