"""Default settings and other constants."""

import logging

from llama_cpp.server.settings import ModelSettings, ServerSettings

__all__ = ["DEFAULT_SERVER_CFG", "PHI3_MODEL_CFG"]

log = logging.getLogger(__name__)

DEFAULT_SERVER_CFG = ServerSettings(
    # api_key="localhost",
)

PHI3_MODEL_CFG = ModelSettings(
    model="./models/Phi-3-mini-4k-instruct-Q8_0.gguf",
    model_alias="phi3",
    n_gpu_layers=-1,
    use_mmap=True,  # auto-detects
    use_mlock=True,  # auto-detects
    n_ctx=4096,
    flash_attn=True,
    cache=True,
    logits_all=True,
    embedding=False,
    chat_format=None,  # force auto-detection
)
