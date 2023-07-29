import re
import warnings
from datetime import datetime
from typing import Optional

from dateutil.parser import ParserError, parse

warnings.filterwarnings("ignore")


class Date:
    """A date object, it is used to store the date of the email and to perform
    some checks on it.

    The focus of the checks is to determine if the date is valid and if it is in the
    correct format.
    The date is valid if it is in the RFC2822 format and if the timezone is valid:

    - [RFC2822](https://tools.ietf.org/html/rfc2822#section-3.3): specifies the
      format of the date in the headers of the mail in the form
      `Day, DD Mon YYYY HH:MM:SS TZ`. Of course it is not the only format used in the
      headers, but it is the most common, so it is the one we use to check if the
      date is valid.
    - [TZ](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones): specifies
      the timezone of the date. We included this check since often malicious emails
      can have a weird behavior, it is not uncommon to see a not existing timezone
      in the headers of the mail (valid timezones are from -12 to +14).

    """

    __raw_date: str
    date: datetime
    __tz: Optional[int]

    def __init__(self, date: str, tz: Optional[int] = None):
        if date is None or date == "":
            raise ValueError("Date cannot be empty or None")
        self.__raw_date = date
        self.date = self.__parse()[0]
        self.__tz = tz

    @property
    def timezone(self) -> int:
        """Get the timezone of the date.

        Returns:
            int: The timezone of the date, if the timezone is not found it returns 0

        """
        if self.__tz is not None:
            return self.__tz

        tz = self.date.tzinfo
        if tz is None:
            return 0

        # remove all non numeric characters exept ":" from the timezone
        clean_tz = re.sub("[^0-9:]", "", str(tz))
        if clean_tz == "":
            return 0

        return int(str(clean_tz).replace("UTC", "").split(":", maxsplit=1)[0])

    @property
    def seconds(self) -> int:
        """Get the seconds of the date."""
        return self.date.second

    @property
    def minutes(self) -> int:
        """Get the minutes of the date."""
        return self.date.minute

    @property
    def hour(self) -> int:
        """Get the hour of the date."""
        return self.date.hour

    @property
    def day(self) -> int:
        """Get the day of the date."""
        return self.date.day

    @property
    def month(self) -> int:
        """Get the month of the date."""
        return self.date.month

    @property
    def year(self) -> int:
        """Get the year of the date. It raises a ValueError if the year is less
        than 1971 since the first email was sent in 1971.

        !!! see
            [history of email](https://en.wikipedia.org/wiki/History_of_email) to know
            more about the first email sent.

        Raises:
            ValueError: If the year is less than 1971

        """
        if self.date.year < 1971:
            raise ValueError("Year cannot be less than 1971")
        return self.date.year

    def __eq__(self, other) -> bool:
        if isinstance(other, Date):
            return self.date.isoformat() == other.date.isoformat()
        if isinstance(other, datetime):
            return self.date.isoformat() == other.isoformat()
        raise TypeError(f"Cannot compare Date with {type(other)}")

    def to_dict(self) -> dict:
        try:
            return {
                "is_RFC_2822": self.is_RFC2822_formatted(),
                "is_tz_valid": self.is_tz_valid(),
                "is_valid": self.is_valid(),
                "date": self.date.isoformat(),
                "posix": self.date.timestamp(),
                "year": self.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "minute": self.minutes,
                "second": self.seconds,
            }
        except:
            return {
                "is_RFC_2822": self.is_RFC2822_formatted(),
                "is_tz_valid": self.is_tz_valid(),
                "is_valid": self.is_valid(),
                "date": self.date.isoformat(),
                "posix": self.date.timestamp(),
                "year": self.date.year,
                "month": self.month,
                "day": self.day,
                "hour": self.hour,
                "minute": self.minutes,
                "second": self.seconds,
            }

    def is_valid(self) -> bool:
        try:
            return (self.is_RFC2822_formatted() and self.is_tz_valid()
                    and self.year >= 1971)
        except ValueError:
            return False

    def __parse(self) -> tuple[datetime, bool]:
        try:
            return datetime.strptime(self.__raw_date, "%a, %d %b %Y %H:%M:%S %z"), True
        except ValueError:
            try:
                return parse(self.__raw_date), False
            except ParserError:
                split_date = self.__raw_date.split(" ")
                reduced_date = " ".join(split_date[0:5])
                return parse(reduced_date), False

    def is_RFC2822_formatted(self) -> bool:
        """Check if the date is in the
        [RFC2822](https://tools.ietf.org/html/rfc2822#section-3.3) format.
        """
        return self.__parse()[1]

    def is_tz_valid(self) -> bool:
        """The timezone is valid if it is in the range [-12, 14]"""
        return -12 <= self.timezone <= 14

    def __repr__(self) -> str:
        return f"{self.date.isoformat()}"
