import re
from os import path

# wordlist source: https://gist.github.com/prasidhda/13c9303be3cbc4228585a7f1a06040a3
WORDLIST = path.join(path.curdir, 'word_blacklist.txt')
DOMAIN_REGEX = re.compile(r"([A-Za-z0-9]+\.)+[A-Za-z]{2,6}")