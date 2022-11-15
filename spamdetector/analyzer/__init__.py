"""
The package contains the main classes and functions used to analyze the emails.
"""

from spamdetector.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer
from spamdetector.analyzer.utils import get_domain, inspect_headers, inspect_body, inspect_attachments

__all__ = [Domain, MailAnalysis, MailAnalyzer, get_domain, inspect_attachments, inspect_body, inspect_headers]