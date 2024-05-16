"""does nlp."""

import asyncio
import json
import logging
import re

from exllamav2.generator import ExLlamaV2Sampler
from exllamav2.generator.filters import ExLlamaV2PrefixFilter
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.exllamav2 import ExLlamaV2TokenEnforcerFilter
from pydantic import BaseModel

from .exl2 import (
    JH_SAMPLING,
    PHI3_EOS_IDS,
    load_exl2_model_dir,
    phi3_prompt_formatter,
    stream_generate,
)

log = logging.getLogger(__name__)


class Character(BaseModel):
    tool: str
    target: str
    heading: int


parser = JsonSchemaParser(Character.model_json_schema())

generator = load_exl2_model_dir("models/bartowski_Phi-3-mini-4k-instruct-exl2")
model, tokenizer = generator.model, generator.tokenizer
generator.set_stop_conditions([tokenizer.eos_token_id, *PHI3_EOS_IDS])
sampling = ExLlamaV2Sampler.Settings(
    **JH_SAMPLING,
    filters=[
        ExLlamaV2PrefixFilter(model, tokenizer, "{"),
        ExLlamaV2TokenEnforcerFilter(parser, tokenizer),
    ],
)
# idk what dataclass bug causes this not to be picked up.
sampling.filter_prefer_eos = True

# NOTE: JSON schema tends to confuse models unless you give examples. Perhaps, giving
# solely examples is better.
sys_prompt = (
    "Your job is to convert audio transcripts into commands for controlling a civilian self-defence system.\n"
    "These audio transcripts suffer from a noisy environment and radio noise, hence you should use your expertise to fill in the gaps as needed.\n"
    "From each transcript, you will extract three things:\n"
    '- "heading": an integer representing the direction to aim.\n'
    '- "tool": the specific tool to deploy for defence.\n'
    '- "target": the target to aim at.\n'
    "If you can't find any of the above, you should infer them from the context.\n"
    "Reply with only the JSON object in accordance to the schema provided below:\n"
    f"{json.dumps(Character.model_json_schema())}"
)


async def nlp_magic(sentence: str):
    # enables `response_model` in create call
    # initialised

    prompt = phi3_prompt_formatter(
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": sentence},
    )

    raw = await asyncio.to_thread(stream_generate, prompt, generator, sampling)

    try:
        # Fix the number including leading zeros...
        raw = re.sub(r"\b0+(\d+)", r"\1", raw)
        resp = Character.model_validate_json(raw)
    except Exception as e:
        raise e
        log.error(f'"{sentence}" failed.', exc_info=e)
        return Character(tool="", target="", heading=0)

    return resp


if __name__ == "__main__":
    import csv

    import pandas as pd

    df = pd.read_csv("data.csv")
    transcript_list = df["transcript"].tolist()

    output_list = []
    failed_list = []
    counter = 1
    list_size = len(transcript_list)
    for transcript in transcript_list:
        ouput = nlp_magic(transcript).model_dump()
        print(f"{ouput}........{counter}/{list_size} Done")
        output_list.append(ouput)
        counter += 1

        if ouput == {"tool": "", "target": "", "heading": 0}:
            failed_list.append(transcript)
            with open("mycsvfile.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(failed_list)
