import pytest
from datetime import timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from utils import fetch_metadata, parse_time_from_str, determine_window, validate_url


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


class TestFetchMetadata:
    def _mock_response(self, html: str, status_code: int = 200):
        response = MagicMock()
        response.text = html
        response.raise_for_status = MagicMock()
        client = AsyncMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        client.get = AsyncMock(return_value=response)
        return client

    @pytest.mark.asyncio
    async def test_extracts_og_title(self):
        html = '<meta property="og:title" content="The Godfather" />'
        with patch("utils.httpx.AsyncClient", return_value=self._mock_response(html)):
            title = await fetch_metadata("https://www.imdb.com/title/tt0068646")
        assert title == "The Godfather"

    @pytest.mark.asyncio
    async def test_raises_when_og_title_missing(self):
        html = "<html><head></head></html>"
        with patch("utils.httpx.AsyncClient", return_value=self._mock_response(html)):
            with pytest.raises(ValueError):
                await fetch_metadata("https://www.imdb.com/title/tt0068646")


class TestValidateUrl:
    def test_valid_imdb(self):
        assert validate_url("https://www.imdb.com/title/tt1234567")

    def test_valid_letterboxd(self):
        assert validate_url("https://letterboxd.com/film/the-godfather")

    def test_rejects_wrong_domain(self):
        assert not validate_url("https://rottentomatoes.com/m/the_godfather")

    def test_rejects_imdb_missing_tt(self):
        assert not validate_url("https://www.imdb.com/title/1234567")

    def test_rejects_plain_string(self):
        assert not validate_url("the godfather")

    def test_rejects_http(self):
        assert not validate_url("http://www.imdb.com/title/tt1234567")
