"""NLP Manager."""

import logging
import re
import time
from typing import Tuple

from exllamav2.generator import ExLlamaV2Sampler
from exllamav2.generator.filters import ExLlamaV2PrefixFilter
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.exllamav2 import ExLlamaV2TokenEnforcerFilter
from word2number.w2n import word_to_num

from .exl2 import load_exl2_model_dir, stream_generate
from .prompt import EXAMPLES, SYS_PROMPT
from .structs import Command, CommandJSON
from .values import (
    CHEESE_SET,
    EXTRA_EOS_TOKENS,
    JH_SAMPLING,
    MODEL_PATH,
    PLACEHOLDER,
    PROMPT_FORMATTER,
)

__all__ = ["NLPManager"]

log = logging.getLogger(__name__)


def check_digit(word: str) -> Tuple[bool, int | None]:
    # handle edge case "niner"
    if word == "niner":
        return True, 9
    try:
        n = word_to_num(word)
    except:
        return False, None
    if len(str(n)) == 1:
        return True, int(n)
    return False, None


def cheese_heading(transcript: str):
    streak = []
    words = re.sub(r"[^a-z0-9]", " ", transcript.lower()).split()
    for word in words:
        is_digit, n = check_digit(word)
        # Sequence too long
        if is_digit and len(streak) == 3:
            streak = []
            continue
        elif is_digit:
            streak.append(str(n))
        elif len(streak) == 3:
            break
        # TODO: Skip/filter stopwords like "uhhh" which may break up the streak.
        else:
            streak = []
    if len(streak) == 3:
        return "".join(streak)
    return None


def cheese_transcript(transcript: str):
    arr = ""
    for word in transcript.split():
        w, p = word.lower(), None
        if not w[-1].isalpha():  # Last char might be punctuation.
            w, p = w[:-1], w[-1]
        if len(w) < 3:
            arr += f" {word}"
        elif w not in CHEESE_SET and not (w[-1] == "s" and w[:-1] in CHEESE_SET):
            arr += f" {word}"
        elif p is not None:
            arr += p
    return arr


class NLPManager:
    """NLP Manager."""

    def __init__(self):
        """Init."""
        parser = JsonSchemaParser(Command.model_json_schema())

        generator = load_exl2_model_dir(MODEL_PATH)
        model, tokenizer = generator.model, generator.tokenizer
        generator.set_stop_conditions([tokenizer.eos_token_id, *EXTRA_EOS_TOKENS])
        sampling = ExLlamaV2Sampler.Settings(
            **JH_SAMPLING,
            filters=[
                ExLlamaV2PrefixFilter(model, tokenizer, "{"),
                ExLlamaV2TokenEnforcerFilter(parser, tokenizer),
            ],
        )
        # idk what dataclass bug causes this not to be picked up.
        sampling.filter_prefer_eos = True

        self.generator = generator
        self.sampling = sampling

    async def extract(self, transcript: str) -> CommandJSON:
        """Extract JSON command."""
        transcript = cheese_transcript(transcript)

        prompt = PROMPT_FORMATTER(
            {"role": "system", "content": SYS_PROMPT},
            *EXAMPLES,
            {"role": "user", "content": transcript},
        )

        # raw = await asyncio.to_thread(stream_generate, prompt, generator, sampling)
        raw = await stream_generate(prompt, self.generator, self.sampling)
        t_post_start = time.time()

        raw = re.sub(r"\b0+(\d+)", r"\1", raw)  # remove leading zeros

        try:
            obj = Command.model_validate_json(raw)
        except Exception as e:
            raise e
            log.error(f'"{transcript}" failed.', exc_info=e)
            return PLACEHOLDER

        # Post-processing
        heading = f"{obj.heading:03d}"[-3:]
        tool = obj.tool.strip()
        tool = tool if tool.isupper() else tool.lower()  # handle EMP
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

        # CHEESE HEADING
        cheese = cheese_heading(transcript)
        heading = heading if cheese is None else cheese

        dur_post = time.time() - t_post_start
        if dur_post > 0.01:
            log.info(f"Post-process: {dur_post:.2f} s")

        return {
            "heading": heading,
            "tool": tool,
            "target": target,
        }


if __name__ == "__main__":
    import csv

    import pandas as pd

    nlp = NLPManager()

    df = pd.read_csv("data.csv")
    transcript_list = df["transcript"].tolist()

    output_list = []
    failed_list = []
    counter = 1
    list_size = len(transcript_list)
    for transcript in transcript_list:
        ouput = nlp.extract(transcript)
        print(f"{ouput}........{counter}/{list_size} Done")
        output_list.append(ouput)
        counter += 1

        if ouput == {"tool": "", "target": "", "heading": 0}:
            failed_list.append(transcript)
            with open("mycsvfile.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(failed_list)
