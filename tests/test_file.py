import os

from app import file

def test_open_wordlist():
    with open(os.path.join(os.path.curdir, 'word_blacklist.txt'), 'r') as f:
        test_list = f.read().splitlines()
        wordlist = file.get_wordlist_from_file('assets/word_blacklist.txt')
        assert wordlist == test_list