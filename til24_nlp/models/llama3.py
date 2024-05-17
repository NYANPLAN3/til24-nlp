"""Phi-3 model."""

from ..structs import Msg

__all__ = ["phi3_prompt_formatter", "PHI3_EOS_IDS"]

PHI3_EOS_IDS = (32000, 32001, 32007)


def phi3_prompt_formatter(*msgs: Msg) -> str:
    """Format messages for prompt."""
    arr = []
    for m in msgs:
        role, content = m["role"], m["content"]
        if role == "system":
            # arr.append(f"<|system|>\n{content}<|end|>\n")
            # See https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/discussions/51
            arr.append(f"<|user|>\n{content}<|end|>\n")
        elif role == "user":
            arr.append(f"<|user|>\n{content}<|end|>\n")
        elif role == "bot":
            arr.append(f"<|assistant|>\n{content}<|end|>\n")
    arr.append("<|assistant|>\n")
    return "".join(arr)
