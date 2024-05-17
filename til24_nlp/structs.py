"""Types."""

import json
from typing import List, Literal, TypedDict

from pydantic import BaseModel

__all__ = [
    "ExtractEntry",
    "ExtractRequest",
    "Msg",
    "Command",
    "COMMAND_SCHEMA",
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


class Command(BaseModel):
    """Command schema.

    Note, instead of matching the competition schema, we use a schema that is easier
    for the model, then calculate the competition schema from it using smart observations.

    NVM, it made things worse, Phi-3 can't do lists of colors apparently.
    """

    heading: int
    tool: str
    target: str
    # target_colors: List[str]


COMMAND_SCHEMA = f"{json.dumps(Command.model_json_schema())}"


class CommandJSON(TypedDict):
    """Actual competition schema."""

    heading: str
    tool: str
    target: str
