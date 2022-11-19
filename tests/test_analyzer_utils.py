import mailparser
import pytest
import spamdetector.analyzer.utils as utils
from spamdetector.analyzer.data_structures import Domain

trustable_mail = mailparser.parse_from_file('tests/samples/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email')
spam = mailparser.parse_from_file('tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email')


class TestInspectHeaders:

    with open('conf/word_blacklist.txt') as f:
        wordlist = f.read().splitlines()

    h_tuple = utils.inspect_headers(trustable_mail.headers, wordlist)
    b_tuple = utils.inspect_headers(spam.headers, wordlist)

    def test_inspect_headers_method(self):
        assert type(self.h_tuple) == tuple
        with pytest.raises(IndexError):
            self.h_tuple[7]

    def test_inspect_headers_in_secure_email(self):
        # spf
        assert self.h_tuple[0] is True
        # dkim
        assert self.h_tuple[1] is True
        # dmarc
        assert self.h_tuple[2] is True
        # same domain in from and received headers
        assert self.h_tuple[3] is True
        # authentication warnig
        assert self.h_tuple[4] is False
        # has suspect subject
        assert self.h_tuple[5] is False
        # send_date
        assert self.h_tuple[6] == 2021

    def test_inspect_headers_in_spam(self):
        # spf
        assert self.b_tuple[0] is False
        # dkim
        assert self.b_tuple[1] is False
        # dmarc
        assert self.b_tuple[2] is False
        # same domain in from and received headers
        assert self.b_tuple[3] is False
        # authentication warnig
        assert self.b_tuple[4] is False
        # has suspect subject
        assert self.b_tuple[5] is False
        # send_date
        assert self.b_tuple[6] < 2015


class TestInspectBody:
    with open('conf/word_blacklist.txt') as f:
        wordlist = f.read().splitlines()

    b_tuple = utils.inspect_body(trustable_mail.body, domain=Domain('github.com'), wordlist=wordlist)

    def test_inspect_body_method(self):
        assert type(self.b_tuple) == tuple
        with pytest.raises(IndexError):
            self.b_tuple[5]

    def test_inspect_body_in_secure_email(self):
        # has http links
        assert self.b_tuple[0] == False
        # has scripts
        assert self.b_tuple[1] == False
        # forbidden words percentage
        assert self.b_tuple[2] == 0.0
        # has form
        assert self.b_tuple[3] == False


def test_spf_pass():
    assert utils.spf_pass(trustable_mail.headers) is True
    assert utils.spf_pass(spam.headers) is False

def test_dkim_pass():
    assert utils.dkim_pass(trustable_mail.headers) is True
    assert utils.dkim_pass(spam.headers) is False

def test_dmarc_pass():
    assert utils.dmarc_pass(trustable_mail.headers) is True
    assert utils.dmarc_pass(spam.headers) is False

def test_get_domain():
    unknown_domain = 'the domain is unknown'
    real_domain = 'the domain is google.com'
    ip_address = '127.0.0.1'

    assert utils.get_domain(unknown_domain) == Domain('unknown')
    assert utils.get_domain(real_domain) == Domain('google.com')
    assert utils.get_domain(ip_address) == Domain('localhost')

def test_script_tag():
    secure_string = '<p>this string is secure</p>'
    falsy_unsecure_string = 'string with script'
    unsecure_string = 'a malicious executable script <script>function foo() {}</script>'

    assert utils.has_script_tag(secure_string) is False
    assert utils.has_script_tag(falsy_unsecure_string) is False
    assert utils.has_script_tag(unsecure_string) is True

def test_http_links():
    assert True is False

def test_has_html():
    html_text = '<html><body><p>some text</p></body></html>'
    plain_text = 'this is a plain text'
    
    assert utils.has_html(html_text) is True
    assert utils.has_html(plain_text) is False

def test_forbidden_words():
    forbidden_words = ['egg', 'spam']
    body = 'a string of trustable words'
    spam = 'spam is not a funny thing'

    assert utils.percentage_of_bad_words(body, forbidden_words) == 0
    assert utils.percentage_of_bad_words(spam, forbidden_words) > 0
