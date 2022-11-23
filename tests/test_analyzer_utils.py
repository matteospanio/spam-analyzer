import mailparser
import pytest
import spamdetector.analyzer.utils as utils
from spamdetector.analyzer.data_structures import Domain

trustable_mail = mailparser.parse_from_file('tests/samples/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email')
spam = mailparser.parse_from_file('tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email')


class TestInspectHeaders:

    with open('conf/word_blacklist.txt') as f:
        wordlist = f.read().splitlines()

    headers_ok = utils.inspect_headers(trustable_mail.headers, wordlist)
    bad_headers = utils.inspect_headers(spam.headers, wordlist)

    def test_inspect_headers_method(self):
        assert type(self.headers_ok) == dict
        with pytest.raises(KeyError):
            self.headers_ok[7]

    def test_inspect_headers_in_secure_email(self):
        assert self.headers_ok["has_spf"] is True
        assert self.headers_ok["has_dkim"] is True
        assert self.headers_ok["has_dmarc"] is True
        assert self.headers_ok["domain_matches"] is True
        assert self.headers_ok["auth_warn"] is False
        assert self.headers_ok["has_suspect_subject"] is False
        assert self.headers_ok["send_date"] == 2021

    def test_inspect_headers_in_spam(self):
        assert self.bad_headers["has_spf"] is False
        assert self.bad_headers["has_dkim"] is False
        assert self.bad_headers["has_dmarc"] is False
        assert self.bad_headers["domain_matches"] is False
        assert self.bad_headers["auth_warn"] is False
        assert self.bad_headers["has_suspect_subject"] is False
        assert self.bad_headers["send_date"] < 2015


class TestInspectBody:

    with open('conf/word_blacklist.txt') as f:
        wordlist = f.read().splitlines()

    body_ok = utils.inspect_body(trustable_mail.body, domain=Domain('github.com'), wordlist=wordlist)

    def test_inspect_body_method(self):
        assert type(self.body_ok) == dict
        with pytest.raises(KeyError):
            self.body_ok[5]

    def test_inspect_body_in_secure_email(self):
        assert self.body_ok["has_links"] is True
        assert self.body_ok["has_mailto"] is False
        assert self.body_ok["https_only"] is False
        assert self.body_ok["contains_script"] is False
        assert self.body_ok["forbidden_words_percentage"] == 0.0
        assert self.body_ok["contains_form"] is False
        assert self.body_ok["contains_html"] is False


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


class TestStringAnalysis:

    html_text = '<html><body><p>some text</p></body></html>'
    html_form = '<form action="https://github.com" method="post"><input type="text" name="username" /></form>'
    plain_text = 'this is a plain text'
    unsecure_string = 'a malicious executable script <script>function foo() {}</script>'
    image_string = 'this is <img src="https://github.com" />'
    empty_string = ''

    def test_has_html(self):
        assert utils.has_html(self.empty_string) is False
        assert utils.has_html(self.html_text) is True
        assert utils.has_html(self.plain_text) is False
        assert utils.has_html(self.html_form) is True
        assert utils.has_html(self.image_string) is True

    def test_has_html_form(self):
        assert utils.has_html_form(self.empty_string) is False
        assert utils.has_html_form(self.html_form) is True
        assert utils.has_html_form(self.html_text) is False
        assert utils.has_html_form(self.plain_text) is False

    def test_script_tag(self):
        assert utils.has_script_tag(self.empty_string) is False
        assert utils.has_script_tag(self.plain_text) is False
        assert utils.has_script_tag(self.html_text) is False
        assert utils.has_script_tag(self.unsecure_string) is True

    def test_parse_html(self):
        assert utils.parse_html(self.empty_string) == ''
        assert utils.parse_html(self.html_text) == 'some text'
        assert utils.parse_html(self.plain_text) == 'this is a plain text'
    
    def test_has_images(self):
        assert utils.has_images(self.empty_string) is False
        assert utils.has_images(self.html_text) is False
        assert utils.has_images(self.plain_text) is False
        assert utils.has_images(self.html_form) is False
        assert utils.has_images(self.image_string) is True


class TestLinks:

    def test_https_only(self):
        empty_list = []
        mixed_links = ['https://github.com', 'http://github.com']
        https_links = ['https://github.com', 'https://google.com']
        assert utils.https_only(mixed_links) is False
        assert utils.https_only(https_links) is True
        assert utils.https_only(empty_list) is False

    def test_get_links(self):
        empty_body = ''
        fake_links = utils.get_links_from_str(empty_body)
        links = utils.get_links_from_str(trustable_mail.body)
        assert type(links) == list
        assert len(links) == 1
        assert fake_links == []
    
    def test_check_links(self):
        links = utils.check_links(trustable_mail.body)
        assert utils.check_links(links['has_links']) is True
        assert utils.check_links(links['mailto']) is False
        assert utils.check_links(links['https_only']) is False

def test_forbidden_words():
    forbidden_words = ['egg', 'spam']
    body = 'a string of trustable words'
    spam = 'spam is not a funny thing'

    assert utils.percentage_of_bad_words(body, forbidden_words) == 0
    assert utils.percentage_of_bad_words(spam, forbidden_words) > 0

def test_inspect_attachments():
    assert utils.inspect_attachments(trustable_mail.attachments)["has_attachments"] is False
    assert utils.inspect_attachments(trustable_mail.attachments)["attachment_is_executable"] is False
    assert utils.inspect_attachments(spam.attachments)["has_attachments"] is False
    assert utils.inspect_attachments(spam.attachments)["attachment_is_executable"] is False