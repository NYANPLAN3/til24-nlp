"""Utility stuff."""

import json

__all__ = ["pp_json"]


def pp_json(data: dict) -> str:
    """Pretty print JSON."""
    # return json.dumps(data, indent=2, separators=(",", ": "))
    return json.dumps(data, separators=(",", ":"))
