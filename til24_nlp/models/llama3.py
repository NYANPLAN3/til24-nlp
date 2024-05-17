"""Llama-3 model."""

from ..structs import Msg

__all__ = ["llama3_prompt_formatter", "LLAMA3_EOS_IDS"]

LLAMA3_EOS_IDS = (128001, 128009)


def encode(msg: Msg) -> str:
    """Encode a message."""
    return f'<|start_header_id|>{msg["role"]}<|end_header_id|>\n\n{msg["content"]}<|eot_id|>'


def llama3_prompt_formatter(*msgs: Msg, is_last=False) -> str:
    """Format messages for prompt."""
    if is_last:
        return encode(msgs[0]) + "<|start_header_id|>assistant<|end_header_id|>\n\n"
    return "<|begin_of_text|>" + "".join(encode(m) for m in msgs)
