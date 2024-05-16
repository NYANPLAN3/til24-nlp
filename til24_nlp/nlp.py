"""does nlp."""

import asyncio
import logging
import re
import time

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


class Command(BaseModel):
    """Command schema.

    Note, instead of matching the competition schema, we use a schema that is easier
    for the model, then calculate the competition schema from it using smart observations.

    NVM, it made things worse, Phi-3 can't do lists of colors apparently.
    """

    heading: int
    tool: str
    target: str
    # target_colors: List[str]


parser = JsonSchemaParser(Command.model_json_schema())

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

# TODO: Consider CoT or other pre-prompt techniques? Effect on speed...
# NOTE: JSON schema tends to confuse models unless you give examples. Perhaps, giving
# solely examples is better.
sys_prompt = (
    "Your role is to convert audio transcripts into commands for a civilian defence turret "
    "which has multiple tools at its disposal. "
    # "The audio transcripts are low quality due to background noise and radio static, hence use your expertise to fill in the gaps. "
    "For each transcript, you will extract ad verbatim:\n"
    '- "heading" (int): direction to aim.\n'
    '- "tool" (str): weapon to use.\n'
    '- "target" (str): target to hit.\n'
    # '- "target_colors" (List[str]): color(s)(if any) of target in original order.\n'
    # "If you cannot find any of the above, you should infer them from the context. "
    # 'For "tool", omit action verbs. '
    # 'You should keep acronyms as acronyms and nouns as nouns without paraphrasing or substituting. '
    # 'For "target", do not paraphrase or use synonyms. '
    # 'For "target_colors", list the colors in the order they appear, ignoring colors '
    # "that do not refer to the target. Leave empty if no colors refer to the target. "
    "Output only JSON objects."
    # "Reply with only the JSON object in accordance to the schema provided below:\n"
    # f"{json.dumps(Command.model_json_schema())}"
)

examples = [
    # Cases: ad verbatim.
    {
        "role": "user",
        "content": "Turret, lock onto target, silver and yellow light aircraft, at three five zero. Deploy electromagnetic pulse.",
    },
    {
        "role": "bot",
        "content": '{"heading":350,"tool":"electromagnetic pulse","target":"silver and yellow light aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above correct answer extracts "electromagnetic pulse" ad verbatim instead of substituting its acronym.',
    },
    {
        "role": "user",
        "content": "Engage target one, silver, green, and orange cargo aircraft with EMP. Heading zero zero five over.",
    },
    {
        "role": "bot",
        "content": '{"heading":005,"tool":"EMP","target":"silver, green, and orange cargo aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above correct answer extracts "EMP" ad verbatim instead of substituting its full form.',
    },
    # Case: unnecessary suffix.
    {
        "role": "user",
        "content": "Activate machine gun system, target the yellow, white, and orange fighter plane heading two niner five. Engage at will.",
    },
    {
        "role": "bot",
        "content": '{"heading":295,"tool":"machine gun","target":"yellow, white, and orange fighter plane"}',
    },
    {
        "role": "system",
        "content": 'Above correct answer discards the unnecessary suffix of "system".',
    },
    # Case: plurality.
    {
        "role": "user",
        "content": "Block black, red, and purple missile at two four five degrees with surface-to-air missiles.",
    },
    {
        "role": "bot",
        "content": '{"heading":245,"tool":"surface-to-air missiles","target":"black, red, and purple missile"}',
    },
    {
        "role": "system",
        "content": 'Above correct answer maintains the plurality of "surface-to-air missiles".',
    },
]


async def nlp_magic(sentence: str):
    # enables `response_model` in create call
    # initialised

    prompt = phi3_prompt_formatter(
        {"role": "system", "content": sys_prompt},
        *examples,
        {"role": "user", "content": sentence},
    )

    raw = await asyncio.to_thread(stream_generate, prompt, generator, sampling)
    # raw = stream_generate(prompt, generator, sampling)
    raw = re.sub(r"\b0+(\d+)", r"\1", raw)  # remove leading zeros

    t_post_start = time.time()
    try:
        obj = Command.model_validate_json(raw)
    except Exception as e:
        # raise e
        log.error(f'"{sentence}" failed.', exc_info=e)
        return dict(
            heading="005", tool="electromagnetic pulse", target="commercial aircraft"
        )

    # Post-processing
    heading = f"{obj.heading:03d}"[-3:]
    tool = obj.tool.strip()
    target = obj.target.strip().lower()
    # colors = [color.strip().lower() for color in obj.target_colors]

    # resp = {}
    # resp["heading"] = heading
    # resp["tool"] = tool if tool.isupper() else tool.lower()  # handle EMP
    # if len(colors) == 0:
    #     resp["target"] = target
    # elif len(colors) == 1:
    #     resp["target"] = f"{colors[0]} {target}"
    # elif len(colors) == 2:
    #     resp["target"] = f"{colors[0]} and {colors[1]} {target}"
    # else:
    #     resp["target"] = f"{', '.join(colors[:-1])}, and {colors[-1]} {target}"

    resp = {
        "heading": heading,
        "tool": tool if tool.isupper() else tool.lower(),  # handle EMP
        "target": target,
    }

    dur_post = time.time() - t_post_start
    log.info(f"Post-process: {dur_post:.2f} s")

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
