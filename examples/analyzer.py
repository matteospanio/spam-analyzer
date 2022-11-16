from spamdetector.analyzer import MailAnalysis, MailAnalyzer

# create a MailAnalysis object passing a wordlist of forbidden words
# to detect in the mail body and subject
analysis_factory = MailAnalyzer(wordlist=['spam', 'phishing', 'malware'])

# the MailAnalyzer outputs a MailAnalysis storing all
# the information from headers, body and attachments inspection
analysis: MailAnalysis = analysis_factory.analyze('path/to/mail')
