import pytest
from datetime import timedelta, timezone
from unittest.mock import patch, MagicMock
from utils import parse_time_from_str, determine_window


class TestParseTimeFromStr:
    def test_minutes(self):
        assert parse_time_from_str("30m") == timedelta(minutes=30)

    def test_hours(self):
        assert parse_time_from_str("1h") == timedelta(hours=1)

    def test_days(self):
        assert parse_time_from_str("7d") == timedelta(days=7)

    def test_multi_digit(self):
        assert parse_time_from_str("90m") == timedelta(minutes=90)

    def test_invalid_unit(self):
        with pytest.raises(ValueError):
            parse_time_from_str("10s")

    def test_invalid_format(self):
        with pytest.raises((ValueError, IndexError)):
            parse_time_from_str("abc")


class TestDetermineWindow:
    def test_minutes_window(self):
        start, end = determine_window(timedelta(minutes=30))
        assert end - start == timedelta(minutes=30)

    def test_hours_window(self):
        start, end = determine_window(timedelta(hours=1))
        assert end - start == timedelta(hours=1)

    def test_days_window(self):
        start, end = determine_window(timedelta(days=7))
        assert end - start == timedelta(days=7)
