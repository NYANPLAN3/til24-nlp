"""All the cheesy stuff."""

import re
from typing import Tuple

from word2number.w2n import word_to_num

from .values import CHEESE_SET, ENABLE_CHEESE

__all__ = ["cheese_heading", "cheese_transcript", "target_from_colors"]


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


def cheese_heading(transcript: str):
    """Extract heading based off sequence of 3 digits."""
    if not ENABLE_CHEESE:
        return None

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
    """Remove words that often trip up the model."""
    if not ENABLE_CHEESE:
        return transcript

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
