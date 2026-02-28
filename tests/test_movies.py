import pytest

from movies import Movie, MovieList


def make_movie(n: int) -> Movie:
    return Movie(name=f"Movie {n}", url=f"https://example.com/{n}")


class TestMovieList:
    @pytest.mark.asyncio
    async def test_add(self):
        ml = MovieList()
        await ml.add(make_movie(1))
        assert len(ml._movies) == 1

    @pytest.mark.asyncio
    async def test_clear(self):
        ml = MovieList()
        await ml.add(make_movie(1))
        await ml.clear()
        assert len(ml._movies) == 0
