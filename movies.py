"""
Movie list and data model
"""

import asyncio
from dataclasses import dataclass


@dataclass
class Movie:
    name: str
    url: str


class MovieList:
    def __init__(self):
        self._movies: list[Movie] = []
        self._lock = asyncio.Lock()

    async def add(self, movie: Movie):
        async with self._lock:
            self._movies.append(movie)

    async def clear(self):
        async with self._lock:
            self._movies.clear()

    def all(self) -> list[Movie]:
        return list(self._movies)
