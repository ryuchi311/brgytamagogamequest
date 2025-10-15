"""Stubs for `telegram.ext` used by the project for static analysis.
These are NOT full implementations. Install `python-telegram-bot` for runtime.
"""
from typing import Any, Callable

class Application:
    @staticmethod
    def builder():
        class _B:
            def token(self, t: str):
                return self
            def build(self):
                return Application()
        return _B()

class CommandHandler:
    def __init__(self, command: str, callback: Callable[..., Any]):
        pass

class CallbackQueryHandler:
    def __init__(self, callback: Callable[..., Any]):
        pass

class ContextTypes:
    class DEFAULT_TYPE:
        pass

class filters:
    text = None
    command = None

__all__ = [
    "Application",
    "CommandHandler",
    "CallbackQueryHandler",
    "ContextTypes",
    "filters",
]
