"""
Scheduler - Async task scheduling (cron-like)
"""

import asyncio
from typing import Callable, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import anyio

from .bus import EventBus, Event, EventType


@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    name: str
    func: Callable
    interval_seconds: float
    last_run: Optional[datetime] = None
    enabled: bool = True


class Scheduler:
    """
    Async scheduler for background tasks
    Emits events to the bus, not just prints
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._task_group: Optional[anyio.abc.TaskGroup] = None

    async def start(self):
        """Start the scheduler"""
        self._running = True
        # Scheduler will be started in background by the OS

    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._task_group:
            self._task_group.cancel_scope.cancel()

    def register_task(
        self,
        name: str,
        func: Callable,
        interval_seconds: float
    ):
        """
        Register a task to run at intervals

        Args:
            name: Task name
            func: Async function to execute
            interval_seconds: Interval between executions
        """
        task = ScheduledTask(
            name=name,
            func=func,
            interval_seconds=interval_seconds
        )
        self.tasks[name] = task

    async def run_scheduler_loop(self):
        """Main scheduler loop"""
        async with anyio.create_task_group() as tg:
            self._task_group = tg

            while self._running:
                now = datetime.now()

                for task in self.tasks.values():
                    if not task.enabled:
                        continue

                    should_run = (
                        task.last_run is None or
                        (now - task.last_run).total_seconds() >= task.interval_seconds
                    )

                    if should_run:
                        tg.start_soon(self._run_task, task)
                        task.last_run = now

                await anyio.sleep(1)  # Check every second

    async def _run_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            result = await task.func()

            # Emit event to bus
            event = Event(
                type=EventType.SYSTEM_EVENT,
                data={
                    "source": "scheduler",
                    "task": task.name,
                    "result": result
                }
            )
            await self.event_bus.publish(event)

        except Exception as e:
            # Emit error event
            event = Event(
                type=EventType.SYSTEM_EVENT,
                data={
                    "source": "scheduler",
                    "task": task.name,
                    "error": str(e)
                }
            )
            await self.event_bus.publish(event)
