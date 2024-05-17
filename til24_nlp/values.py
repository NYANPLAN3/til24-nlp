"""All hardcoded constants."""

__all__ = [
    "JH_SAMPLING",
    "MODEL_PATH",
    "EXTRA_EOS_TOKENS",
    "PLACEHOLDER",
    "PROMPT_FORMATTER",
]

from .models.llama3 import LLAMA3_EOS_IDS, llama3_prompt_formatter
from .models.phi3 import PHI3_EOS_IDS, phi3_prompt_formatter

PLACEHOLDER = {
    "heading": 5,
    "tool": "electromagnetic pulse",
    "target": "commercial aircraft",
}

# TODO: Consider contrastive/tree/branch sampling? How?
# See ExLlamaV2Sampler.Settings().
JH_SAMPLING = dict(
    temperature=0.05,  # 0.7
    # temperature_last=True,
    top_k=50,
    top_p=1.0,
    token_repetition_penalty=1.0,  # 1 = no penalty
)

CHEESE_SET = {
    "hostile",
    "turret",
    "system",
    "cluster",
    "weapon",
    "device",
    "unit",
    "strike",
    "defence",
    "defense",
    "countermeasure",
}


MODEL_PATH = "models/bartowski_Phi-3-mini-4k-instruct-exl2"
EXTRA_EOS_TOKENS = PHI3_EOS_IDS
PROMPT_FORMATTER = phi3_prompt_formatter

# MODEL_PATH = "models/bartowski_Meta-Llama-3-8B-Instruct-exl2"
# EXTRA_EOS_TOKENS = LLAMA3_EOS_IDS
# PROMPT_FORMATTER = llama3_prompt_formatter
