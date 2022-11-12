import os

from app.files import get_wordlist_from_file

def test_open_wordlist():
    with open(os.path.join(os.path.curdir, 'assets/word_blacklist.txt'), 'r') as f:
        test_list = f.read().splitlines()
        wordlist = get_wordlist_from_file('assets/word_blacklist.txt')
        assert wordlist == test_list