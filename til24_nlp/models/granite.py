"""IBM Granite model."""

from ..structs import Msg

__all__ = ["granite_prompt_formatter", "GRANITE_EOS_IDS"]

GRANITE_EOS_IDS = (0,)


def encode(msg: Msg) -> str:
    """Encode a message."""
    if msg["role"] == "system":
        return f'System:\n{msg["content"]}\n\n'
    elif msg["role"] == "user":
        return f'Question:\n{msg["content"]}\n\n'
    elif msg["role"] == "assistant":
        return f'Answer:\n{msg["content"]}\n\n'
    else:
        assert False, f"Granite cannot support arbitrary roles."


def granite_prompt_formatter(*msgs: Msg, is_last=False) -> str:
    """Format messages for prompt."""
    if is_last:
        return encode(msgs[0]) + "Answer:\n"
    return "<|endoftext|>" + "".join(encode(m) for m in msgs)
