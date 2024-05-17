"""Llama-3 model."""

from ..structs import Msg

__all__ = ["llama3_prompt_formatter", "LLAMA3_EOS_IDS"]

LLAMA3_EOS_IDS = (128001, 128009)


def llama3_prompt_formatter(*msgs: Msg) -> str:
    """Format messages for prompt."""
    arr = ["<|begin_of_text|>"]
    for m in msgs:
        role, content = m["role"], m["content"]
        arr.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>")
    arr.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n")
    return "".join(arr)
