class EmailError(Exception):
    """Base class for exceptions in this module."""


class EmailFormatError(EmailError):
    """Exception raised for errors in the email format."""

    def __init__(self, message="The email format is not valid"):
        self.message = message
        super().__init__(self.message)
