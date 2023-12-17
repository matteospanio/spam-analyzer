import asyncio
import os
from typing import Tuple

import pytest

from spamanalyzer.data_structures import MailAnalysis, SpamAnalyzer
from spamanalyzer.domain import Domain

SAMPLES_FOLDER = "tests/samples"

ham = os.path.join(
    SAMPLES_FOLDER,
    "97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email",
)
spam = os.path.join(
    SAMPLES_FOLDER,
    "00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email",
)

with open("src/app/conf/word_blacklist.txt", "r", encoding="utf-8") as f:
    wordlist = f.read().splitlines()


@pytest.fixture
async def analysis() -> Tuple[MailAnalysis, MailAnalysis]:
    analyzer = SpamAnalyzer(wordlist)

    return await asyncio.gather(analyzer.analyze(ham), analyzer.analyze(spam))


class TestSpamAnalyzer:
    analyzer = SpamAnalyzer(wordlist)

    @pytest.mark.asyncio
    async def test_get_domain(self):
        assert (await self.analyzer.get_domain(ham)
                ) == Domain("github-lowworker-5fb2734.va3-iad.github.net")

    @pytest.mark.asyncio
    async def test_mail_analysis_is_spam(self, analysis):
        assert self.analyzer.is_spam(analysis[0]) is False

    @pytest.mark.asyncio
    async def test_multiple_analysis(self, analysis):
        ham, spam = analysis
        assert self.analyzer.classify_multiple_input([ham, spam]) == [
            False,
            True,
        ]


class TestMailAnalysis:

    @pytest.mark.asyncio
    async def test_mail_analysis_type(self, analysis):
        ham, _ = analysis
        assert isinstance(ham, MailAnalysis)

    @pytest.mark.asyncio
    async def test_mail_analysis_file_path(self, analysis):
        assert analysis[0].file_path == ham

    @pytest.mark.asyncio
    async def test_to_dict(self, analysis):
        dict_mail = analysis[0].to_dict()
        assert isinstance(dict_mail, dict)
        assert isinstance(dict_mail["body"], dict)
        with pytest.raises(KeyError):
            assert dict_mail["is_spam"] is None
            assert dict_mail["not_existing_key"] is None
