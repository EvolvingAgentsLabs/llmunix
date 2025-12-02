"""
Watchdog - Monitor LLM execution and prevent loops/hallucinations
"""

import asyncio
from typing import Optional
import anyio

from .bus import EventBus, Event, EventType


class Watchdog:
    """
    Watchdog to monitor LLM execution
    Prevents infinite loops and hallucinations
    """

    def __init__(self, event_bus: EventBus, timeout_seconds: float = 60.0):
        self.event_bus = event_bus
        self.timeout_seconds = timeout_seconds
        self._active = False
        self._timer_task: Optional[anyio.abc.CancelScope] = None

    async def start(self):
        """Start watchdog monitoring"""
        pass  # Watchdog is activated on-demand

    async def stop(self):
        """Stop watchdog monitoring"""
        if self._timer_task:
            self._timer_task.cancel()

    async def activate(self):
        """Activate watchdog timer for LLM execution"""
        self._active = True

        async with anyio.create_task_group() as tg:
            self._timer_task = tg.cancel_scope

            async def timer():
                await anyio.sleep(self.timeout_seconds)
                if self._active:
                    # Emit interrupt event
                    event = Event(
                        type=EventType.INTERRUPT,
                        data={
                            "source": "watchdog",
                            "reason": "timeout",
                            "timeout_seconds": self.timeout_seconds
                        }
                    )
                    await self.event_bus.publish(event)

            tg.start_soon(timer)

    async def deactivate(self):
        """Deactivate watchdog timer"""
        self._active = False
        if self._timer_task:
            self._timer_task.cancel()
