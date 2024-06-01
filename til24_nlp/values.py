"""All hardcoded constants."""

__all__ = [
    "JH_SAMPLING",
    "MODEL_PATH",
    "EXTRA_EOS_TOKENS",
    "PLACEHOLDER",
    "ENABLE_RISKY_CHEESE",
    "ENABLE_CHEESE_HEADING",
    "ENABLE_CHEESE_SKIP_HEADING",
    "ENABLE_CHEESE_FILTER_TRANSCRIPT",
    "ENABLE_CHEESE_HARD_CASES",
    "DISABLE_CHEESE_PLURALITY",
    "PROMPT_FORMATTER",
]

from exllamav2.generator import ExLlamaV2Sampler

from .models.granite import GRANITE_EOS_IDS, granite_prompt_formatter
from .models.llama3 import LLAMA3_EOS_IDS, llama3_prompt_formatter
from .models.phi3 import PHI3_EOS_IDS, phi3_prompt_formatter

PLACEHOLDER = {
    "heading": "005",
    "tool": "electromagnetic pulse",
    "target": "commercial aircraft",
}

# TODO: Consider contrastive/tree/branch sampling? How?
# See ExLlamaV2Sampler.Settings().
# JH_SAMPLING = dict(
#     temperature=0,  # 0.7 # NOTE: avoid too small in case of NaN
#     # temperature_last=True,
#     top_k=50,
#     top_p=1.0,
#     token_repetition_penalty=1.0,  # 1 = no penalty
# )
JH_SAMPLING = ExLlamaV2Sampler.Settings.greedy()

DEBUG_PREVIEW = False

# Enable/disable all risky cheeses.
ENABLE_RISKY_CHEESE = True

# Enable/disable individual risky cheeses.
ENABLE_CHEESE_HEADING = True
ENABLE_CHEESE_SKIP_HEADING = False
ENABLE_CHEESE_FILTER_TRANSCRIPT = True

# Disable safe cheeses.
DISABLE_CHEESE_PLURALITY = False
ENABLE_CHEESE_HARD_CASES = True


MODEL_PATH = "models/bartowski_Phi-3-mini-4k-instruct-exl2"
EXTRA_EOS_TOKENS = PHI3_EOS_IDS
PROMPT_FORMATTER = phi3_prompt_formatter

# MODEL_PATH = "models/Interpause_granite-3b-code-instruct-exl2"
# EXTRA_EOS_TOKENS = GRANITE_EOS_IDS
# PROMPT_FORMATTER = granite_prompt_formatter

# MODEL_PATH = "models/bartowski_Meta-Llama-3-8B-Instruct-exl2"
# EXTRA_EOS_TOKENS = LLAMA3_EOS_IDS
# PROMPT_FORMATTER = llama3_prompt_formatter
