import asyncio
from spamanalyzer import MailAnalysis, MailAnalyzer


async def spam_analysis():
    analysis_factory = MailAnalyzer(wordlist=["spam", "phishing", "malware"])
    analysis: MailAnalysis = await analysis_factory.analyze("path/to/mail")

    return analysis


analysis = asyncio.run(spam_analysis())
print(analysis)
