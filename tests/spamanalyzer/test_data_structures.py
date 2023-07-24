import asyncio
import os
import pytest
from typing import Tuple
from spamanalyzer.data_structures import (
    MailAnalysis,
    MailAnalyzer,
)
from spamanalyzer.domain import Domain
from app.files import handle_configuration_files

SAMPLES_FOLDER = "tests/samples"

trustable_mail = os.path.join(
    SAMPLES_FOLDER,
    "97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email",
)
spam = os.path.join(
    SAMPLES_FOLDER,
    "00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email",
)

with open("src/app/conf/word_blacklist.txt", "r", encoding="utf-8") as f:
    wordlist = f.read().splitlines()

_, _, _ = handle_configuration_files()


class TestMailAnalyzer:

    @pytest.mark.asyncio
    async def test_get_domain(self):
        analyzer = MailAnalyzer(wordlist)
        assert (await analyzer.get_domain(trustable_mail)
                ) == Domain("github-lowworker-5fb2734.va3-iad.github.net")


@pytest.fixture
async def analysis() -> Tuple[MailAnalysis, MailAnalysis]:
    analyzer = MailAnalyzer(wordlist)

    return await asyncio.gather(analyzer.analyze(trustable_mail),
                                analyzer.analyze(spam))


class TestMailAnalysis:
    analyzer = MailAnalyzer(wordlist)

    @pytest.mark.asyncio
    async def test_mail_analysis_type(self, analysis):
        ham, _ = analysis
        assert isinstance(ham, MailAnalysis)

    @pytest.mark.asyncio
    async def test_mail_analysis_file_path(self, analysis):
        assert analysis[0].file_path == trustable_mail

    @pytest.mark.asyncio
    async def test_mail_analysis_is_spam(self, analysis):
        assert analysis[0].is_spam() is False

    @pytest.mark.asyncio
    async def test_multiple_analysis(self, analysis):
        ham, spam = analysis
        assert MailAnalysis.classify_multiple_input([ham, spam]) == [
            False,
            True,
        ]

    @pytest.mark.asyncio
    async def test_to_dict(self, analysis):
        dict_mail = analysis[0].to_dict()
        assert isinstance(dict_mail, dict)
        assert dict_mail["file_name"] == trustable_mail
        assert dict_mail["is_spam"] is False
        with pytest.raises(KeyError):
            assert dict_mail["not_existing_key"] is None
