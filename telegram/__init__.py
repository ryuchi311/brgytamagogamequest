"""Minimal runtime stubs for `telegram` to satisfy static analysis in the editor.
These are intentionally light-weight and only meant to allow imports and basic type hints.
Do NOT rely on these for runtime behavior — install the real `python-telegram-bot` in production or Docker containers.
"""
from typing import Any

class _Me:
    username: str = "bot"
    first_name: str = "Bot"

class Bot:
    def __init__(self, token: str | None = None, **kwargs: Any) -> None:
        self.token = token

    async def get_me(self) -> _Me:  # pragma: no cover - stub
        return _Me()

class Update:
    pass

class InlineKeyboardButton:
    def __init__(self, text: str = "", callback_data: str | None = None):
        self.text = text
        self.callback_data = callback_data

class InlineKeyboardMarkup:
    def __init__(self, keyboard: list | None = None):
        self.keyboard = keyboard or []

# Common constants used by some bots
ParseMode = None

__all__ = ["Bot", "Update", "InlineKeyboardButton", "InlineKeyboardMarkup", "ParseMode"]
