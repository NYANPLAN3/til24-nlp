"""All the cheesy stuff."""

import logging
import random
import re
from itertools import combinations
from typing import List

from word2number.w2n import word_to_num

from .colorcorrection import replace_misheard_colors
from .structs import Command, CommandJSON
from .values import *

__all__ = [
    "cheese_heading",
    "cheese_filter_transcript",
    "cheese_tool_plurality",
    "cheese_target_plurality",
    "target_from_colors",
    "preprocess",
    "postprocess",
]

log = logging.getLogger(__name__)


def _convert_digit(word: str) -> int | str:
    """Check if word is a digit."""
    # handle edge case "niner"
    if word == "niner":
        return 9
    try:
        n = word_to_num(word)
    except:
        return word
    if len(str(n)) == 1:
        return int(n)
    return word


MISHEARD_MAP = {
    "none": 1,
    "wan": 1,
    "to": 2,
    "too": 2,
    "tree": 3,
    "for": 4,
    "fore": 4,
    "fiver": 5,
    "sex": 6,
    "sick": 6,
    "sever": 7,
    "ate": 8,
    "aid": 8,
}


def _valid(h: str):
    return 0 <= int(h) <= 360


def _repair_heading(ori: List[int | str], seq: str, is2=False) -> str | None:
    ### Cases with too many numbers ###
    # Case: Perfect 3-streak
    if m := re.search(r"(?<!\d)(\d{3})(?!\d)", seq):
        if _valid(h := m.group(1)):
            return h

    # Case: "to ddd"
    if m := re.search(r"(?<!\d)2(\d{3})(?!\d)", seq):
        if _valid(h := m.group(1)):
            return h
    # Case: "ddd to"
    if m := re.search(r"(?<!\d)(\d{3})2(?!\d)", seq):
        if _valid(h := m.group(1)):
            return h

    # Case: "for ddd"
    if m := re.search(r"(?<!\d)4(\d{3})(?!\d)", seq):
        if _valid(h := m.group(1)):
            return h
    # Case: "ddd for"
    if m := re.search(r"(?<!\d)(\d{3})4(?!\d)", seq):
        if _valid(h := m.group(1)):
            return h

    # NOTE: 5-streak alr very unlikely, any longer & we risk false positive on adversarial cases like phone numbers.
    # Case: Perfect 4/5-streak find plausible heading
    if m := re.search(r"(?<!\d)(\d{4,5})(?!\d)", seq):
        possible = ["".join(l) for l in combinations(m.group(1), 3)]
        valid = [h for h in possible if _valid(h)]
        if len(valid) > 0:
            return random.choice(valid)

    # NOTE: Disabled else it will false positive for phone number case.
    # Case: Loose 3-streak
    # if m := re.search(r"\D*(\d{3})\D*", seq):
    #     if _valid(h := m.group(1)):
    #         return h

    ### Cases with too little numbers ###
    # Case: dXd
    if m := re.search(r"(?<!\d)(\d)(X)(\d)(?!\d)", seq):
        if (w := ori[m.start(2)]) in MISHEARD_MAP:
            if _valid(h := f"{m.group(1)}{MISHEARD_MAP[w]}{m.group(3)}"):
                return h

    # Case: Xdd
    if m := re.search(r"(?<!\d)(X)(\d{2})(?!\d)", seq):
        if (w := ori[m.start(1)]) in MISHEARD_MAP:
            if _valid(h := f"{MISHEARD_MAP[w]}{m.group(2)}"):
                return h

    # Case: ddX
    if m := re.search(r"(?<!\d)(\d{2})(X)(?!\d)", seq):
        if (w := ori[m.start(2)]) in MISHEARD_MAP:
            if _valid(h := f"{m.group(1)}{MISHEARD_MAP[w]}"):
                return h

    # Case: dXdd
    if m := re.search(r"(?<!\d)(\d)X(\d{2})(?!\d)", seq):
        if _valid(h := f"{m.group(1)}{m.group(2)}"):
            return h

    # Case: ddXd
    if m := re.search(r"(?<!\d)(\d{2})X(\d)(?!\d)", seq):
        if _valid(h := f"{m.group(1)}{m.group(2)}"):
            return h

    # Case: GG
    if is2:
        return None  # Give up.
    rep = [MISHEARD_MAP.get(w, w) for w in ori]
    repseq = "".join(str(w) if isinstance(w, int) else "X" for w in rep)
    return _repair_heading(rep, repseq, is2=True)


def cheese_heading(transcript: str):
    """Extract heading based off sequence of 3 digits."""
    if not ENABLE_RISKY_CHEESE or not ENABLE_CHEESE_HEADING:
        return None

    words = re.sub(r"[^a-z0-9]", " ", transcript.lower()).split()
    ori = [_convert_digit(w) for w in words]
    seq = "".join(str(w) if isinstance(w, int) else "X" for w in ori)

    # TODO: Is risky, but consider pre-removing number streaks that are too long?
    # i.e., phone numbers, coordinates, etc.
    return _repair_heading(ori, seq)


# TODO: Pretty sure these won't accidentally remove valid answers even for openset, right?
FILTER_SET = {
    "hostile",
    "turret",
    "system",
    "strike",
    "cluster",
    "weapon",
    "weaponry",
    "device",
    "unit",
    "defence",
    "defense",
    "countermeasure",
}


def cheese_filter_transcript(transcript: str):
    """Remove words that often trip up the model."""
    if not ENABLE_RISKY_CHEESE or not ENABLE_CHEESE_FILTER_TRANSCRIPT:
        return transcript

    out = ""
    for word in transcript.split():
        w, p = word.lower(), None
        if not w[-1].isalpha():  # Last char might be punctuation.
            w, p = w[:-1], w[-1]
        if len(w) < 3:
            out += f" {word}" if len(out) > 0 else word
        elif w not in FILTER_SET and not (w[-1] == "s" and w[:-1] in FILTER_SET):
            out += f" {word}" if len(out) > 0 else word
        elif p is not None and len(out) > 0:  # Don't add punc if 1st word.
            out += p
    return out


def cheese_tool_plurality(tool: str):
    """Auto-correct plurality based on last word."""
    # Is always safe & hard to prompt for, so ENABLE_CHEESE doesn't control this.
    if DISABLE_CHEESE_PLURALITY:
        return tool

    if tool.endswith(("missile", "jet")):
        return tool + "s"
    elif tool.endswith(("missiles", "jets")):
        return tool
    elif tool.endswith("ries"):
        return tool[:-3] + "y"
    elif tool.endswith("s"):
        return tool[:-1]
    return tool


def cheese_target_plurality(target: str):
    """Auto-correct plurality based on last word."""
    # Is always safe & hard to prompt for, so ENABLE_CHEESE doesn't control this.
    if DISABLE_CHEESE_PLURALITY:
        return target

    # NOTE: THE RULES FOR TARGET & TOOL ARE DIFFERENT. ITS ALWAYS SINGULAR HERE.
    if target.endswith("ries"):
        return target[:-3] + "y"
    elif target.endswith("s"):
        return target[:-1]
    return target


# NOTE: This didn't work well, so its unused.
def target_from_colors(colors: list[str], target: str) -> str:
    """Combine colors with target."""
    if len(colors) == 0:
        return target
    if len(colors) == 1:
        return f"{colors[0]} {target}"
    if len(colors) == 2:
        return f"{colors[0]} and {colors[1]} {target}"
    return f"{', '.join(colors[:-1])}, and {colors[-1]} {target}"


def preprocess(transcript: str):
    """Preprocess transcript."""
    transcript = cheese_filter_transcript(transcript)
    if ENABLE_CHEESE_HARD_CASES:
        transcript = transcript.replace("electromagnetic pulse (EMP)", "EMP")
        transcript = transcript.replace("EMP missiles", "EMP")
        transcript = transcript.replace("EMP missile", "EMP")
    return transcript


# fmt: off
TARGET_CORRECTION_MAP = {
    "jet": ["jetty", "jett", "jit"],
    "drone": ["throne", "phone"],
    "plane": ["plank", "pipeline", "jane", "maine", "pane", "pain"],
    "missile": ["missal", "mistle", "miss hill", "miss sell", "muscle"],
    "aircraft": ["air craft", "air raft", "ear craft", "hair craft", "care craft", "airshaft", "air shaft"],
    "helicopter": ["heli copter", "helly copter", "hell o copter", "holy copter", "heli hopper", "telecaster"],
    "cargo": ["car go", "car glow", "car gold", "car grow", "car goal"],
    # "commercial": ["commer seal", "comm er cial", "commersial", "commer she al", "comm her cial"],
}
# fmt: on

TOOL_CORRECTION_MAP = {
    "gun": ["fun", "run"],
    "drone": ["throne", "phone"],
    "catcher": ["snatcher", "matcher", "latcher", "etcher"],
    "missiles": ["missals", "mistles", "miss hills", "miss sells", "muscles"],
    "jets": ["jetty", "jett", "jit"],
}


def postprocess(transcript: str, obj: Command):
    """Postprocess transcript."""
    heading = int("".join(c for c in obj.heading if c.isnumeric()))
    heading = f"{heading:03d}"[-3:]
    tool = obj.tool.strip()
    tool = tool if tool.isupper() else tool.lower()  # handle EMP
    target = obj.target.strip().lower()
    if COLOR_CORRECTION_ON:
        target = replace_misheard_colors(target)

    if FIX_TARGET_ON:
        for correct, wrongs in TARGET_CORRECTION_MAP.items():
            for wrong in wrongs:
                target = re.sub(rf"\b{wrong}s?\b", correct, target)

    if FIX_TOOL_ON:
        for correct, wrongs in TOOL_CORRECTION_MAP.items():
            for wrong in wrongs:
                tool = re.sub(rf"\b{wrong}s?\b", correct, tool)

    cheese = cheese_heading(transcript)
    heading = heading if cheese is None else cheese
    tool = cheese_tool_plurality(tool)
    target = cheese_target_plurality(target)
    return CommandJSON(heading=heading, tool=tool, target=target)


if __name__ == "__main__":
    transcripts = [
        "Control to turret, prepare to engage red helicopter at heading four zero six five.",
        "Engage the yellow drone with surface-to-air missiles, heading two two three five.",
        "Deploy electromagnetic pulse, heading one one zero four turrets on aircraft",
        "Control to turrets, heading one one zero two engage aircraft with emp now",
    ]

    for i in range(0, len(transcripts)):
        heading = cheese_heading(transcripts[i])
        print(heading)
