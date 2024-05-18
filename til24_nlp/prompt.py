"""Model prompt."""

from til24_nlp.utils import pp_json

from .structs import COMMAND_SCHEMA

__all__ = ["SYS_PROMPT", "EXAMPLES"]

# TODO: Consider CoT or other pre-prompt techniques? Effect on speed...
# NOTE: JSON schema tends to confuse models unless you give examples. Perhaps, giving
# solely examples is better.
SYS_PROMPT = (
    "Your job is to convert audio transcripts into computer-parsable data for a "
    "civilian defence turret which has multiple tools at its disposal. "
    "Background noise and radio static may have degraded the audio quality of some transcripts. "
    # "The audio transcripts are low quality due to background noise and radio static, hence use your expertise to fill in the gaps. "
    "For each transcript, extract the following information ad verbatim:\n"
    '- "heading" (str): direction to aim as an integer from "000" to "360".\n'
    '- "tool" (str): tool to use.\n'
    '- "target" (str): target\'s type and colours.\n'
    # '- "target_colors" (List[str]): color(s)(if any) of target in original order.\n'
    # "If you cannot find any of the above, you should infer them from the context. "
    # 'For "tool", omit action verbs. '
    # 'You should keep acronyms as acronyms and nouns as nouns without paraphrasing or substituting. '
    # 'For "target", do not paraphrase or use synonyms. '
    # 'For "target_colors", list the colors in the order they appear, ignoring colors '
    # "that do not refer to the target. Leave empty if no colors refer to the target. "
    "Output only the corresponding minified JSON object."
    # "Output only the corresponding JSON object, following the schema provided below:\n"
    # f"{COMMAND_SCHEMA}"
)


def _example(qn: str, ans: str, reason: str):
    return (
        {"role": "user", "content": qn},
        {"role": "assistant", "content": ans},
        {"role": "system", "content": reason},
    )


def _ans(heading: str, tool: str, target: str):
    return pp_json(dict(heading=heading, tool=tool, target=target))


case_verbatim_1 = _example(
    "Engage target one, silver, green, and orange cargo aircraft with EMP countermeasure. Heading zero zero seven over.",
    _ans("007", "EMP", "silver, green, and orange cargo aircraft"),
    'Above answer correctly extracts "EMP" ad verbatim instead of replacing it with "electromagnetic pulse".',
)
case_verbatim_2 = _example(
    "Turret, lock onto target, unfriendly silver and yellow light aircraft, at three five two. Deploy electromagnetic pulse weapon.",
    _ans("352", "electromagnetic pulse", "silver and yellow light aircraft"),
    'Above answer correctly extracts "electromagnetic pulse" ad verbatim instead of replacing it with "EMP".',
)
case_verbatim_3 = _example(
    "Shoot green camouflage APC with torpedo system. Heading three one seven over.",
    _ans("317", "torpedo", "green camouflage APC"),
    'Above answer correctly extracts "APC" ad verbatim instead of replacing it with "armoured personnel carrier".',
)
case_verbatim_4 = _example(
    "Team Alpha, use your LMG to shoot down hostile pink and purple drone cluster at one one three, over.",
    _ans("113", "LMG", "pink and purple drone"),
    'Above answer correctly extracts "LMG" ad verbatim instead of replacing it with "light machine gun".',
)
case_verbatim_5 = _example(
    "Activate light machine gun system, target the dangerous green and red zombie cluster. Heading two zero zero. Engage at will.",
    _ans("200", "light machine gun", "green and red zombie"),
    'Above answer correctly extracts "light machine gun" ad verbatim instead of replacing it with "LMG".',
)
case_suffix_1 = _example(
    "Activate machine gun turret, target the hostile yellow, white, and orange fighter plane heading two niner five. Engage at will.",
    _ans("295", "machine gun", "yellow, white, and orange fighter plane"),
    'Above answer correctly discards the unnecessary suffix of "system".',
)
case_suffix_2 = _example(
    "At one one nine engage red and blue drone cluster with drone catcher.",
    _ans("119", "drone catcher", "red and blue drone"),
    'Above answer correctly discards the unnecessary suffix of "cluster".',
)
case_suffix_3 = _example(
    "Turret Foxtrot, heading zero niner eight, engage white, yellow, and orange light aircraft with machine gun fire.",
    _ans("098", "machine gun", "white, yellow, and orange light aircraft"),
    'Above answer correctly discards the unnecessary suffix of "fire".',
)
case_prefix_1 = _example(
    "Control tower to interceptor jets, scramble immediately. We have an enemy blue, black, and silver cargo aircraft on heading three zero five. Engage and intercept the target. Over.",
    _ans("305", "interceptor jets", "blue, black, and silver cargo aircraft"),
    'Above answer correctly discards the unnecessary prefix of "enemy" which is not part of the target\'s appearance.',
)
case_plurality_1 = _example(
    "Block black, red, and purple missile at two four zero degrees with surface-to-air missiles.",
    _ans("240", "surface-to-air missiles", "black, red, and purple missile"),
    'Above answer correctly maintains the plurality of "surface-to-air missiles".',
)


EXAMPLES = (
    *case_verbatim_1,
    *case_verbatim_2,
    *case_verbatim_3,
    *case_verbatim_4,
    *case_verbatim_5,
    *case_suffix_1,
    *case_suffix_2,
    *case_suffix_3,
    *case_prefix_1,
    # NOTE: THIS EXAMPLE IS A DEALBREAKER IDK WHY. KEEP IT LAST INSPITE OF PLURALITY FIX.
    *case_plurality_1,
)
