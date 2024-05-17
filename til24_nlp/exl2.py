"""Utilities for handling exllamav2."""

import logging
import os
import sys
import time
from typing import Literal

from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Cache,
    ExLlamaV2Cache_8bit,
    ExLlamaV2Cache_Q4,
    ExLlamaV2Config,
    ExLlamaV2Tokenizer,
)
from exllamav2.attn import has_flash_attn
from exllamav2.generator import ExLlamaV2Sampler, ExLlamaV2StreamingGenerator

__all__ = ["load_exl2_model_dir", "stream_generate"]

log = logging.getLogger(__name__)

log.info(f"Flash Attention: {has_flash_attn}")
# NOTE: T4 doesn't support flash attention.
# assert has_flash_attn, "Oh? The eval instance doesn't have flash attention? Debug time."

# Examples used:
# https://github.com/turboderp/exllamav2/blob/master/examples/lm_format_enforcer.py
# https://github.com/noamgat/lm-format-enforcer/blob/main/samples/colab_exllamav2_integration.ipynb
# turboderp is expert on the model loading itself, noamgat is the expert for the grammar.
# So I adapt techniques from both accordingly.


def load_exl2_model_dir(
    dir: str | os.PathLike,
    cache_quant: Literal["None", "Q8", "Q4"] = "None",
):
    """Load exllamav2 model from model directory."""
    dir = dir if isinstance(dir, str) else str(dir)
    log.info(f"Loading exllamav2 model at {dir}")

    cfg = ExLlamaV2Config(dir)
    model = ExLlamaV2(cfg)
    tokenizer = ExLlamaV2Tokenizer(cfg)

    if cache_quant == "Q8":
        log.warning("8-bit KV cache has higher PPL than 4-bit cache")
        cache = ExLlamaV2Cache_8bit(model, lazy=True)
    elif cache_quant == "Q4":
        cache = ExLlamaV2Cache_Q4(model, lazy=True)
    else:
        cache = ExLlamaV2Cache(model, lazy=True)

    model.load_autosplit(cache)
    # NOTE: AFAIK, turboderp used streaming specifically for speculative ngram.
    # Maybe its some optimization for the case of grammar I don't know?
    # TODO: Consider using batching (incompatible with streaming).
    generator = ExLlamaV2StreamingGenerator(model, cache, tokenizer)
    generator.speculative_ngram = True
    generator.warmup()

    return generator


def stream_generate(
    prompt: str,
    generator: ExLlamaV2StreamingGenerator,
    sampling: ExLlamaV2Sampler.Settings,
    max_new_tokens: int = 256,
    preview: bool = False,
):
    """Generate a response."""
    tokenizer = generator.tokenizer

    if preview:
        log.info(f"###PROMPT###\n{prompt}")

    t_prompt_start = time.time()
    # Cache the input_ids for the prompt.
    input_ids = tokenizer.encode(prompt)
    prompt_tokens = input_ids.shape[-1]

    generator.begin_stream_ex(input_ids, sampling)

    t_stream_start = time.time()
    result = []
    while True:
        res = generator.stream_ex()
        chunk, eos = res["chunk"], res["eos"]
        result.append(chunk)
        if preview:
            print(chunk, end="")
            sys.stdout.flush()
        if eos or len(result) >= max_new_tokens:
            break
    if preview:
        print()

    t_end = time.time()

    dur_prompt = t_stream_start - t_prompt_start
    dur_tokens = t_end - t_stream_start

    log.info(
        f"Prompt: {dur_prompt:.2f} s, {prompt_tokens} toks, {prompt_tokens / dur_prompt:.2f} tok/s\n"
        f"Response: {dur_tokens:.2f} s, {len(result)} toks, {len(result) / dur_tokens:.2f} tok/s"
    )

    return "".join(result)
