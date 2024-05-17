"""Types."""

from typing import List

from pydantic import BaseModel

__all__ = ["ExtractEntry", "ExtractRequest", "PLACEHOLDER"]


class ExtractEntry(BaseModel):
    """Text entry."""

    transcript: str


class ExtractRequest(BaseModel):
    """Text to parse into JSON."""

    instances: List[ExtractEntry]


PLACEHOLDER = {
    "heading": "005",
    "tool": "electromagnetic pulse",
    "target": "commercial aircraft",
}
