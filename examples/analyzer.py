import asyncio

from spamanalyzer import MailAnalysis, SpamAnalyzer


async def spam_analysis():
    analysis_factory = SpamAnalyzer(wordlist=["spam", "phishing", "malware"])
    analysis: MailAnalysis = await analysis_factory.analyze("path/to/mail")

    return analysis


analysis = asyncio.run(spam_analysis())
print(analysis)
