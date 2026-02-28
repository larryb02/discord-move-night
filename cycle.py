"""
Movie night planning + voting cycle
"""

from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta, timezone
from typing import Any
import logging
from enum import Enum
import asyncio

from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.get("LOG_LEVEL"))

Callback = Callable[..., Coroutine[Any, Any, None]]


class CycleEvent(Enum):
    NOMINATION_WINDOW_START = 0
    VOTING_WINDOW_START = 1
    VOTING_WINDOW_EXPIRED = 2


class CycleState(Enum):
    IDLE = 0
    NOMINATING = 1
    VOTING = 2
    ANNOUNCING = 3


_TRANSITIONS = {
    (CycleState.IDLE, CycleEvent.NOMINATION_WINDOW_START): CycleState.NOMINATING,
    (CycleState.NOMINATING, CycleEvent.VOTING_WINDOW_START): CycleState.VOTING,
    (CycleState.VOTING, CycleEvent.VOTING_WINDOW_EXPIRED): CycleState.ANNOUNCING,
}


class MovieNightCycle:
    """
    State machine for movie night cycle.
    Callbacks are injected by the caller — no Discord logic here.
    """

    def __init__(
        self,
        nomination_window: timedelta,
        voting_window: timedelta,
        on_nominations_open: Callback | None = None,
        on_voting_open: Callback | None = None,
        on_cycle_complete: Callback | None = None,
    ):
        self.current_state = CycleState.IDLE
        self.nomination_window = nomination_window
        self.voting_window = voting_window
        self.on_nominations_open = on_nominations_open
        self.on_voting_open = on_voting_open
        self.on_cycle_complete = on_cycle_complete
        self._task: asyncio.Task | None = None

    def _transition(self, event: CycleEvent):
        key = (self.current_state, event)
        if key not in _TRANSITIONS:
            raise ValueError(f"Invalid transition: {self.current_state} + {event}")
        self.current_state = _TRANSITIONS[key]
        logger.debug("Transitioning to %s", self.current_state)

    def start(self):
        """
            Start a movie night cycle
        """
        self._task = asyncio.create_task(self._run())

    def cancel(self):
        """
            Cancel a movie night cycle
        """
        if self._task:
            self._task.cancel()
            self._task = None
        self.current_state = CycleState.IDLE
        logger.debug("Cycle cancelled")

    async def _run(self):
        logger.debug("Starting cycle")

        self._transition(CycleEvent.NOMINATION_WINDOW_START)
        deadline = datetime.now(timezone.utc) + self.nomination_window
        if self.on_nominations_open:
            await self.on_nominations_open(deadline)
        await asyncio.sleep(self.nomination_window.total_seconds())

        self._transition(CycleEvent.VOTING_WINDOW_START)
        deadline = datetime.now(timezone.utc) + self.voting_window
        if self.on_voting_open:
            await self.on_voting_open(deadline)
        await asyncio.sleep(self.voting_window.total_seconds())

        self._transition(CycleEvent.VOTING_WINDOW_EXPIRED)
        if self.on_cycle_complete:
            await self.on_cycle_complete()

        logger.debug("Cycle complete")


if __name__ == "__main__":
    logging.basicConfig()

    async def main():
        c = MovieNightCycle(timedelta(seconds=10), timedelta(seconds=5))
        c.start()
        await asyncio.sleep(20)

    asyncio.run(main())
