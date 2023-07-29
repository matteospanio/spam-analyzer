import os

from app.files import file_is_valid_email, get_files_from_dir


def test_get_files_from_directory():
    # should get a list of files from `data` directory
    file_list = get_files_from_dir(os.path.join(os.path.curdir, "tests/samples"))
    test_file = file_list[0]
    assert isinstance(file_list, list)
    assert isinstance(test_file, str)
    assert os.path.isfile(test_file) is True


def test_invalid_email_file():
    assert (file_is_valid_email(
        "tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email"
    ) is True)
    assert file_is_valid_email("tests/samples/invalid_file.txt") is False
