"""All the cheesy stuff."""

import re
from typing import Tuple

from word2number.w2n import word_to_num

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


def check_digit(word: str) -> Tuple[bool, int | None]:
    """Check if word is a digit."""
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

remove_punc = re.compile(r"[^a-z0-9]")


def cheese_heading(transcript: str):
    """Extract heading based off sequence of 3 digits."""
    streak = []
    words = remove_punc.sub(" ", transcript.lower()).split()
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


FILTER_SET = {
    "hostile",
    "turret",
    "system",
    "cluster",
    "weapon",
    "weaponry",
    "device",
    "unit",
    "strike",
    "defence",
    "defense",
    "countermeasure",
}


def cheese_filter_transcript(transcript: str):
    """Remove words that often trip up the model."""
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
    while len(tool) > 0 and not tool[-1].isalpha():
        tool = tool[:-1]
    if len(tool) == 0:
        return ""
    t = tool.lower()
    if t.endswith(("missile", "jet")):
        return tool + "s"
    elif t.endswith(("missiles", "jets")):
        return tool
    elif t.endswith("ries"):
        return tool[:-3] + "y"
    elif t.endswith("s"):
        return tool[:-1]
    elif t == "emp missiles":
        return "EMP"
    return tool



def cheese_target_plurality(target: str):
    """Auto-correct plurality based on last word."""
    if target.endswith("s"):
        return target[:-1]
    return target


# # NOTE: This didn't work well, so its unused.
# def target_from_colors(colors: list[str], target: str) -> str:
#     """Combine colors with target."""
#     if len(colors) == 0:
#         return target
#     if len(colors) == 1:
#         return f"{colors[0]} {target}"
#     if len(colors) == 2:
#         return f"{colors[0]} and {colors[1]} {target}"
#     return f"{', '.join(colors[:-1])}, and {colors[-1]} {target}"

# TOOL_SET = (
#     "electromagnetic pulse",
#     "surface-to-air missiles",
#     "EMP",
#     "machine gun",
#     "anti-air artillery",
#     "interceptor jets",
#     "drone catcher",
# )


# def cheese_tool(transcript: str):
#     """There is a fixed set of tools..."""
#     # stupid case
#     if "(EMP)" in transcript:
#         return "EMP"
#     # First, "fix" the plurality of all words.
#     transcript = " ".join(cheese_tool_plurality(w) for w in transcript.split())
#     idx = 999999
#     ans = "EMP"
#     for tool in TOOL_SET:
#         test = transcript.lower() if tool.islower() else transcript
#         for m in re.finditer(tool, test):
#             i = m.start()
#             if i < idx:
#                 idx = i
#                 ans = tool

#     return ans

# TARGET_SET = ("jet", "drone", "plane", "missile", "aircraft", "helicopter")
# COLOR_SET = {
#     "black",
#     "blue",
#     "brown",
#     "green",
#     "grey",
#     "orange",
#     "purple",
#     "red",
#     "silver",
#     "white",
#     "yellow",
# }
# ADJ_SET = {"and", "camouflage", "cargo", "commercial", "fighter", "light"}


# def remove_tool(tool: str, s: str):
#     """Remove tool from sentence."""
#     if tool.isupper():
#         s = s.replace(tool, " ")
#         s = s.lower()
#     else:
#         s = s.lower()
#         s = s.replace(tool, " ")
#     return s

# def get_target_string(s: str, noun_idx: int):
#     """Given a candidate index, find the full target string."""
#     start_idx = s.rfind(" ", 0, noun_idx)
#     colors = 0
#     while start_idx > 0:
#         next_idx = s.rfind(" ", 0, start_idx)
#         word = s[next_idx:start_idx].strip().replace(",", "")
#         if word in COLOR_SET:
#             start_idx = next_idx
#             colors += 1
#         elif word in ADJ_SET:
#             start_idx = next_idx
#         else:
#             break
#     tgt = s[start_idx:noun_idx].strip()
#     return colors, noun_idx, tgt


# def cheese_target(tool: str, s: str):
#     """Guess target as the earliest valid target string, preferring color over earliness."""
#     s = remove_tool(tool, s)
#     candidates = []
#     for tgt in TARGET_SET:
#         for m in re.finditer(tgt, s):
#             candidates.append(get_target_string(s, m.end()))

#     return sorted(candidates, key=lambda x: (x[0], -x[1]))[-1][-1]

def preprocess(transcript: str):
    """Preprocess transcript."""
    transcript = cheese_filter_transcript(transcript)
    transcript = transcript.replace("electromagnetic pulse (EMP)", "EMP")
    transcript = transcript.replace("EMP missile", "EMP")
    
    return transcript




def postprocess(transcript: str, obj: Command):
    """Postprocess transcript."""
    heading = f"{int(''.join(c for c in obj.heading if c.isnumeric())):03d}"[-3:]
    tool = obj.tool.strip()
    tool = tool if tool.isupper() else tool.lower()  # handle EMP
    target = obj.target.strip().lower()
    # colors = [color.strip().lower() for color in obj.target_colors]

    cheese = cheese_heading(transcript)
    heading = heading if cheese is None else cheese
    tool = cheese_tool_plurality(tool)
 
    
    target = cheese_target_plurality(target)
    return CommandJSON(
        heading=heading,
        tool=tool,
        target=target,
    )
