import os

from app.files import get_files_from_dir

def test_get_files_from_directory():
    # should get a list of files from `data` directory
    file_list = get_files_from_dir(os.path.join(os.path.curdir, 'data'))
    test_file = file_list[0]
    assert type(file_list) == list
    assert type(test_file) == str
    assert os.path.isfile(test_file) is True
