"""All the cheesy stuff."""

import logging
import re

from word2number.w2n import word_to_num

from .structs import Command, CommandJSON
from .values import *
from .colorcorrection import process_text
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


def cheese_heading(transcript: str):
    """Extract heading based off sequence of 3 digits."""
    if not ENABLE_RISKY_CHEESE or not ENABLE_CHEESE_HEADING:
        return None

    words = re.sub(r"[^a-z0-9]", " ", transcript.lower()).split()
    ori = []
    seq = []
    for word in words:
        word_or_n = _convert_digit(word)
        ori.append(word_or_n)
        seq.append(str(word_or_n) if isinstance(word_or_n, int) else "X")
    seq = "".join(seq)  # XXXXXXXX315XXXXXX

    # TODO: Skip/filter stopwords like "uhhh" which may break up the streak.
    heading = None

    # Case: Perfect 3-streak
    if m := re.search(r"(?<!\d)(\d\d\d)(?!\d)", seq):
        heading = m.group(1)

    # Case: "to \d\d\d"
    elif m := re.search(r"(?<!\d)2(\d\d\d)(?!\d)", seq):
        heading = m.group(1)
    # Case: "\d\d\d to"
    elif m := re.search(r"(?<!\d)(\d\d\d)2(?!\d)", seq):
        heading = m.group(1)

    # Case: "for \d\d\d"
    elif m := re.search(r"(?<!\d)4(\d\d\d)(?!\d)", seq):
        heading = m.group(1)
    # Case: "\d\d\d for"
    elif m := re.search(r"(?<!\d)(\d\d\d)4(?!\d)", seq):
        heading = m.group(1)
        
    #case a 2-streak due to misheard numbers d\x\d
    elif re.fullmatch(r"[^0-9]*[0-9]?[^0-9]*[0-9]?[^0-9]*", seq):
        print("The sequence contains less than 3 numbers.")
        # Second pass of the transcript to replace misheard words
        replaced_words = []
        for word in words:
            if word in MISHEARD_MAP:
                replaced_words.append(str(MISHEARD_MAP[word]))
            else:
                replaced_words.append(word)  
        ori = []
        seq = []

        for word in replaced_words:  # Use replaced words in this pass
            word_or_n = _convert_digit(word)
            ori.append(word_or_n)
            seq.append(str(word_or_n) if isinstance(word_or_n, int) else "x")

    
        seq = "".join(seq)  # Create sequence of digits and x


        if re.search(r"\d{4}", seq):  # Check if sequence contains a 4-digit number
            match = re.search(r"\d{4}", seq).group()
            if int(match[0])>3: #case of 4dd2 or any misheard number more than 3
                heading = match[1:]
            elif match[0] == "2": #case of 2dd4
                heading = match[1:]

        else:
            heading = re.search(r"\d{3}", seq).group() # will get smt like x2xx2xxxxx046 but its impossible for 3 consecutive digits to be anywhere else but the heading
 
        

    # Case: Loose 3-streak
    # TODO: for 4-streaks, pick either 111X or X111 depending on which is valid 0 to 360.
    elif m := re.search(r"\D*(\d\d\d)\D*", seq):
        heading = m.group(1)

    # NOTE: These cases must come last to avoid gobbling up the above cases.
    # Case: "\dX\d"
    elif m := re.search(r"(?<!\d)(\d)(X)(\d)(?!\d)", seq):
        w = ori[m.start(2)]
        if w in MISHEARD_MAP:
            heading = f"{m.group(1)}{MISHEARD_MAP[w]}{m.group(3)}"

    try:
        if heading is not None and not (0 <= int(heading) <= 360):
            return None
    except:
        log.error(f"INVALID HEADING: {heading}")
        return None

    return heading


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

    if target.endswith("s"):
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


def postprocess(transcript: str, obj: Command):
    """Postprocess transcript."""
    heading = int(''.join(c for c in obj.heading if c.isnumeric()))
    heading = f"{heading:03d}"[-3:]
    tool = obj.tool.strip()
    tool = tool if tool.isupper() else tool.lower()  # handle EMP
    target = obj.target.strip().lower()
    target = process_text(target)
    
    # colors = [color.strip().lower() for color in obj.target_colors]

    cheese = cheese_heading(transcript)
    heading = heading if cheese is None else cheese
    tool = cheese_tool_plurality(tool)
    target = cheese_target_plurality(target)
    return CommandJSON(heading=heading, tool=tool, target=target)


if __name__ == "__main__":
    
 
    
    transcripts = ["Control to turret, prepare to engage red helicopter at heading four zero six five.",
                   "Engage the yellow drone with surface-to-air missiles, heading two two three five.",
                   "Deploy electromagnetic pulse, heading one one zero four turrets on aircraft",
                   "Control to turrets, heading one one zero two engage aircraft with emp now",]
                   

    for i in range(0,len(transcripts)):
        heading = cheese_heading(transcripts[i])
        print(heading)