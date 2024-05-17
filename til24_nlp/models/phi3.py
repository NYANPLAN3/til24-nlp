"""Phi-3 model."""

from ..structs import Msg

__all__ = ["phi3_prompt_formatter", "PHI3_EOS_IDS"]

PHI3_EOS_IDS = (32000, 32001, 32007)


def encode(msg: Msg) -> str:
    """Encode a message."""
    role, content = msg["role"], msg["content"]
    # See https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/discussions/51
    # role = "user" if role == "system" else role
    return f"<|{role}|>\n{content}<|end|>\n"


def phi3_prompt_formatter(*msgs: Msg, is_last=False) -> str:
    """Format messages for prompt."""
    if is_last:
        return encode(msgs[0]) + "<|assistant|>\n"
    return "<s>" + "".join(encode(m) for m in msgs)
