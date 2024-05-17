"""All hardcoded constants."""

__all__ = [
    "JH_SAMPLING",
    "MODEL_PATH",
    "EXTRA_EOS_TOKENS",
    "PLACEHOLDER",
    "PROMPT_FORMATTER",
]

from .models.phi3 import PHI3_EOS_IDS, phi3_prompt_formatter

PLACEHOLDER = {
    "heading": "005",
    "tool": "electromagnetic pulse",
    "target": "commercial aircraft",
}

# TODO: Consider contrastive/tree/branch sampling? How?
# See ExLlamaV2Sampler.Settings().
JH_SAMPLING = dict(
    temperature=0.0,  # 0.7
    # temperature_last=True,
    top_k=100,
    top_p=1.0,
    token_repetition_penalty=1.0,  # 1 = no penalty
)


MODEL_PATH = "models/bartowski_Phi-3-mini-4k-instruct-exl2"
EXTRA_EOS_TOKENS = PHI3_EOS_IDS
PROMPT_FORMATTER = phi3_prompt_formatter
