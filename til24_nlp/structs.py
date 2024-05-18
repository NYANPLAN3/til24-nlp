"""Types."""

from typing import List, Literal, TypedDict

from pydantic import BaseModel

__all__ = [
    "ExtractEntry",
    "ExtractRequest",
    "Msg",
    "CheeseCommand",
    "Command",
    "CommandJSON",
]


class ExtractEntry(BaseModel):
    """Text entry."""

    transcript: str


class ExtractRequest(BaseModel):
    """Text to parse into JSON."""

    instances: List[ExtractEntry]


class Msg(TypedDict):
    """Type of a message."""

    role: Literal["system", "user", "assistant"]
    content: str


class CheeseCommand(BaseModel):
    tool: str
    target: str


# NOTE: DO NOT PUT A DOCSTRING IT APPEARS IN THE SCHEMA.
class Command(BaseModel):
    heading: str
    tool: str
    target: str
    # target_colors: List[str]


class CommandJSON(TypedDict):
    """Actual competition schema."""

    heading: str
    tool: str
    target: str
