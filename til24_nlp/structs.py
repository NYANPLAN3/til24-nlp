"""Types."""

import json
from typing import List, Literal, TypedDict

from pydantic import BaseModel

from til24_nlp.utils import pp_json

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


# NOTE: DO NOT PUT A DOCSTRING IT APPEARS IN THE SCHEMA.
class Command(BaseModel):
    heading: str
    tool: str
    target: str
    # target_colors: List[str]


COMMAND_SCHEMA = pp_json(Command.model_json_schema())


class CommandJSON(TypedDict):
    """Actual competition schema."""

    heading: str
    tool: str
    target: str
