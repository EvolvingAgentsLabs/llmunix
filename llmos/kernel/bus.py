"""
Event Bus - Pub/Sub communication between components
"""

import asyncio
from enum import Enum
from typing import Any, Callable, Dict, List
from dataclasses import dataclass
import anyio


class EventType(Enum):
    """Event types in the system"""
    USER_INPUT = "user_input"
    SYSTEM_EVENT = "system_event"
    LLM_OUTPUT = "llm_output"
    TOOL_OUTPUT = "tool_output"
    INTERRUPT = "interrupt"
    TIMER = "timer"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"


@dataclass
class Event:
    """Event structure"""
    type: EventType
    data: Any
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class EventBus:
    """
    Event Bus for inter-component communication
    Uses anyio memory object streams for async pub/sub
    """

    def __init__(self):
        self._channels: Dict[EventType, tuple] = {}
        self._subscribers: Dict[EventType, List[Callable]] = {}

    def create_channel(self, event_type: EventType, buffer_size: int = 100):
        """Create a new channel for an event type"""
        send_stream, receive_stream = anyio.create_memory_object_stream(
            max_buffer_size=buffer_size
        )
        self._channels[event_type] = (send_stream, receive_stream)
        self._subscribers[event_type] = []

    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        if event.type not in self._channels:
            self.create_channel(event.type)

        send_stream, _ = self._channels[event.type]
        await send_stream.send(event)

    async def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self._channels:
            self.create_channel(event_type)

        self._subscribers[event_type].append(callback)

    async def start_listeners(self):
        """Start all event listeners"""
        async with anyio.create_task_group() as tg:
            for event_type in self._channels:
                tg.start_soon(self._listener_loop, event_type)

    async def _listener_loop(self, event_type: EventType):
        """Listen for events and dispatch to subscribers"""
        _, receive_stream = self._channels[event_type]

        async for event in receive_stream:
            for callback in self._subscribers.get(event_type, []):
                await callback(event)
