"""
Terminal Input Handler - Cross-platform keyboard input.

Provides non-blocking keyboard input for the terminal UI.
Works on Unix (macOS/Linux) and Windows.
"""

import sys
import asyncio
from typing import Optional, Callable, Awaitable
from enum import Enum


class Key(Enum):
    """Special key codes"""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ENTER = "ENTER"
    TAB = "TAB"
    ESCAPE = "ESCAPE"
    BACKSPACE = "BACKSPACE"
    QUIT = "QUIT"


class InputHandler:
    """
    Cross-platform keyboard input handler.

    Uses termios on Unix and msvcrt on Windows.
    """

    def __init__(self):
        self._old_settings = None
        self._is_windows = sys.platform == "win32"

    def setup(self):
        """Setup terminal for raw input"""
        if self._is_windows:
            # Windows doesn't need setup
            pass
        else:
            # Unix: disable line buffering
            import termios
            import tty
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

    def cleanup(self):
        """Restore terminal settings"""
        if self._is_windows:
            pass
        else:
            if self._old_settings:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)

    def _read_char_unix(self) -> Optional[str]:
        """Read a single character on Unix"""
        import select

        # Check if input is available (non-blocking)
        if select.select([sys.stdin], [], [], 0.1)[0]:
            ch = sys.stdin.read(1)

            # Handle escape sequences (arrow keys)
            if ch == '\x1b':
                # Read the rest of the escape sequence
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            ch3 = sys.stdin.read(1)
                            if ch3 == 'A':
                                return Key.UP.value
                            elif ch3 == 'B':
                                return Key.DOWN.value
                            elif ch3 == 'C':
                                return Key.RIGHT.value
                            elif ch3 == 'D':
                                return Key.LEFT.value
                return Key.ESCAPE.value

            # Handle special keys
            if ch == '\n' or ch == '\r':
                return Key.ENTER.value
            if ch == '\t':
                return Key.TAB.value
            if ch == '\x7f' or ch == '\x08':
                return Key.BACKSPACE.value
            if ch == 'q' or ch == 'Q':
                return Key.QUIT.value

            return ch

        return None

    def _read_char_windows(self) -> Optional[str]:
        """Read a single character on Windows"""
        import msvcrt

        if msvcrt.kbhit():
            ch = msvcrt.getch()

            # Handle special keys
            if ch == b'\xe0' or ch == b'\x00':
                # Extended key
                ch2 = msvcrt.getch()
                if ch2 == b'H':
                    return Key.UP.value
                elif ch2 == b'P':
                    return Key.DOWN.value
                elif ch2 == b'M':
                    return Key.RIGHT.value
                elif ch2 == b'K':
                    return Key.LEFT.value
                return None

            ch = ch.decode('utf-8', errors='ignore')

            if ch == '\r':
                return Key.ENTER.value
            if ch == '\t':
                return Key.TAB.value
            if ch == '\x08':
                return Key.BACKSPACE.value
            if ch == 'q' or ch == 'Q':
                return Key.QUIT.value
            if ch == '\x1b':
                return Key.ESCAPE.value

            return ch

        return None

    def read_key(self) -> Optional[str]:
        """
        Read a single key press (non-blocking).

        Returns:
            Key name or character, or None if no input available
        """
        if self._is_windows:
            return self._read_char_windows()
        else:
            return self._read_char_unix()

    async def read_key_async(self) -> Optional[str]:
        """
        Async version of read_key.

        Returns:
            Key name or character, or None if no input available
        """
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.read_key)


async def run_terminal_loop(
    render_callback: Callable[[], str],
    input_callback: Callable[[str], Awaitable[bool]],
    refresh_callback: Callable[[], Awaitable[None]],
    refresh_interval: float = 5.0
):
    """
    Main terminal loop with input handling.

    Args:
        render_callback: Function that returns the terminal output string
        input_callback: Async function that handles input, returns False to quit
        refresh_callback: Async function to refresh data
        refresh_interval: Seconds between auto-refresh
    """
    handler = InputHandler()
    handler.setup()

    last_refresh = asyncio.get_event_loop().time()

    try:
        # Initial render
        print("\033[2J\033[H", end="")  # Clear screen
        print(render_callback())

        while True:
            # Check for input
            key = handler.read_key()

            if key:
                # Handle input
                should_continue = await input_callback(key)

                if not should_continue:
                    break

                # Re-render after input
                print("\033[2J\033[H", end="")  # Clear screen
                print(render_callback())

            # Auto-refresh
            current_time = asyncio.get_event_loop().time()
            if current_time - last_refresh >= refresh_interval:
                await refresh_callback()
                last_refresh = current_time
                print("\033[2J\033[H", end="")  # Clear screen
                print(render_callback())

            # Small sleep to prevent CPU spinning
            await asyncio.sleep(0.05)

    finally:
        handler.cleanup()
        print("\n👋 Terminal closed.")
