from spamdetector.lib.data_structures import Domain
import spamdetector.lib.utils as utils
import mailparser

trustable_mail = mailparser.parse_from_file('data/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539')
spam = mailparser.parse_from_file('data/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a')

def test_inspect_headers():
    assert False is True

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

def test_inspect_body():
    assert True is False

def test_script_tag():
    secure_string = '<p>this string is secure</p>'
    falsy_unsecure_string = 'string with script'
    unsecure_string = 'a malicious executable script <script>function foo() {}</script>'

    assert utils.has_script_tag(secure_string) is False
    assert utils.has_script_tag(falsy_unsecure_string) is False
    assert utils.has_script_tag(unsecure_string) is True

def test_http_links():
    assert True is False

def test_forbidden_words():
    forbidden_words = ['egg', 'spam']
    body = 'a string of trustable words'
    spam = 'spam is not a funny thing'

    assert utils.contains_forbidden_words(body, forbidden_words) is False
    assert utils.contains_forbidden_words(spam, forbidden_words) is True
