import asyncio
from datetime import timedelta

import pytest

from cycle import CycleState, MovieNightCycle

SHORT = timedelta(seconds=0.05)
LONG = timedelta(hours=1)


class TestCancel:
    @pytest.mark.asyncio
    async def test_cancel_during_nominations(self):
        c = MovieNightCycle(LONG, LONG)
        c.start()
        await asyncio.sleep(0)  # yield so task starts
        assert c.current_state == CycleState.NOMINATING
        c.cancel()
        assert c.current_state == CycleState.IDLE
        assert c._task is None

    @pytest.mark.asyncio
    async def test_cancel_during_voting(self):
        c = MovieNightCycle(SHORT, LONG)
        c.start()
        await asyncio.sleep(SHORT.total_seconds() + 0.05)
        assert c.current_state == CycleState.VOTING
        c.cancel()
        assert c.current_state == CycleState.IDLE
        assert c._task is None

    @pytest.mark.asyncio
    async def test_cancel_before_start_is_safe(self):
        c = MovieNightCycle(LONG, LONG)
        c.cancel()  # should not raise
        assert c.current_state == CycleState.IDLE
