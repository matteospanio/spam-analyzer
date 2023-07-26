import datetime

import pytest
from dateutil.parser import parse

from spamanalyzer.date import Date


class TestDate:
    RFC_date = "Wed, 17 Feb 2021 10:00:00 +0100"
    invalid_date = "Wed, 17 Feb 2021 10:00:00"
    date_plus_0 = "Wed, 17 Feb 2021 10:00:00 +0000"
    invalid_utc = "Wed, 17 Feb 2021 10:00:00 +1900"
    empty_date = ""

    def test_successful_date_creation(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)

        assert date1.date == parse(self.RFC_date)
        assert date2.date == parse(self.invalid_date)

    def test_RFC_2822_format(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)
        date3 = Date(self.invalid_utc)

        assert date1.is_RFC2822_formatted() is True
        assert date2.is_RFC2822_formatted() is False
        assert date3.is_RFC2822_formatted() is True

    def test_is_tz_valid(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)
        date3 = Date(self.invalid_utc)

        assert date1.is_tz_valid() is True
        assert date2.is_tz_valid() is True
        assert date3.is_tz_valid() is False

    def test_empty_date_creation(self):
        with pytest.raises(ValueError):
            Date(self.empty_date)

    def test_equality(self):
        date_datetime = datetime.datetime.strptime(self.RFC_date,
                                                   "%a, %d %b %Y %H:%M:%S %z")

        assert Date(self.RFC_date) == Date(self.RFC_date)
        assert Date(self.RFC_date) != Date(self.invalid_date)
        assert Date(self.RFC_date) == date_datetime
        with pytest.raises(TypeError):
            assert Date(self.RFC_date) == 1

    def test_timezone(self):
        assert Date(self.RFC_date).timezone == 1
        assert Date(self.date_plus_0).timezone == 0
        assert Date(self.invalid_utc).timezone == 19
