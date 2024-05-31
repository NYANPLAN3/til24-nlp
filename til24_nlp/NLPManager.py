"""NLP Manager."""

import logging
import re
import time

from exllamav2.generator import ExLlamaV2Sampler
from exllamav2.generator.filters import ExLlamaV2PrefixFilter
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.exllamav2 import ExLlamaV2TokenEnforcerFilter

from .cheese import postprocess, preprocess
from .exl2 import load_exl2_model_dir, stream_generate
from .prompt import EXAMPLES, SYS_PROMPT
from .structs import CheeseCommand, Command, CommandJSON
from .values import (
    ENABLE_CHEESE_SKIP_HEADING,
    EXTRA_EOS_TOKENS,
    JH_SAMPLING,
    MODEL_PATH,
    PLACEHOLDER,
    PROMPT_FORMATTER,
)

__all__ = ["NLPManager"]

log = logging.getLogger(__name__)

CMD_CLS = CheeseCommand if ENABLE_CHEESE_SKIP_HEADING else Command


class NLPManager:
    """NLP Manager."""

    def __init__(self):
        """Init."""
        parser = JsonSchemaParser(CMD_CLS.model_json_schema())

        generator = load_exl2_model_dir(MODEL_PATH)
        model, tokenizer = generator.model, generator.tokenizer
        generator.set_stop_conditions([tokenizer.eos_token_id, *EXTRA_EOS_TOKENS])
        sampling = ExLlamaV2Sampler.Settings(
            **JH_SAMPLING,
            filters=[
                ExLlamaV2PrefixFilter(model, tokenizer, '{"'),
                # ExLlamaV2PrefixFilter(model, tokenizer, '{\n'),
                ExLlamaV2TokenEnforcerFilter(parser, tokenizer),
            ],
        )
        # idk what dataclass bug causes this not to be picked up.
        sampling.filter_prefer_eos = True

        preprompt = PROMPT_FORMATTER(
            {"role": "system", "content": SYS_PROMPT},
            *EXAMPLES,
        )
        log.info(f"###PRE###\n{preprompt}")

        self.generator = generator
        self.sampling = sampling
        self.pre_toks = tokenizer.encode(preprompt, encode_special_tokens=True)
        # print(np.array2string(self.pre_toks.numpy()[0], threshold=np.inf))

    def extract(self, transcript: str) -> CommandJSON:
        """Extract JSON command."""
        # Pre-processing.
        t_pre_start = time.time()
        transcript = preprocess(transcript)
        prompt = PROMPT_FORMATTER({"role": "user", "content": transcript}, is_last=True)
        dur_pre = time.time() - t_pre_start
        if dur_pre > 0.01:
            log.info(f"Pre-process: {dur_pre:.2f} s")

        # Processing.
        raw = stream_generate(
            prompt, self.generator, self.sampling, pre_toks=self.pre_toks
        )
        t_post_start = time.time()

        try:
            raw = re.sub(r"\b0+(\d+)", r"\1", raw)  # remove leading zeros
            obj = CMD_CLS.model_validate_json(raw)
        except Exception as e:
            # raise e
            log.error(f'"{transcript}" failed.', exc_info=e)
            obj = Command.model_validate(PLACEHOLDER)

        if isinstance(obj, CheeseCommand):
            obj = Command(
                heading=PLACEHOLDER["heading"], tool=obj.tool, target=obj.target
            )

        # Post-processing.
        cmd_dict = postprocess(transcript, obj)
        dur_post = time.time() - t_post_start
        if dur_post > 0.01:
            log.info(f"Post-process: {dur_post:.2f} s")

        return cmd_dict


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
   

