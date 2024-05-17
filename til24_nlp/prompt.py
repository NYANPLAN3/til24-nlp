"""Model prompt."""

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
    '- "heading" (int): direction to aim as a positive integer.\n'
    '- "tool" (str): type of weapon to use.\n'
    '- "target" (str): appearance and type of target to hit.\n'
    # '- "target_colors" (List[str]): color(s)(if any) of target in original order.\n'
    # "If you cannot find any of the above, you should infer them from the context. "
    # 'For "tool", omit action verbs. '
    # 'You should keep acronyms as acronyms and nouns as nouns without paraphrasing or substituting. '
    # 'For "target", do not paraphrase or use synonyms. '
    # 'For "target_colors", list the colors in the order they appear, ignoring colors '
    # "that do not refer to the target. Leave empty if no colors refer to the target. "
    # "Output only JSON objects."
    "Output only the corresponding JSON object, following the schema provided below:\n"
    f"{COMMAND_SCHEMA}"
)

EXAMPLES = (
    # Cases: ad verbatim.
    {
        "role": "user",
        "content": "Engage target one, silver, green, and orange cargo aircraft with EMP countermeasure. Heading zero zero seven over.",
    },
    {
        "role": "assistant",
        "content": '{"heading":007,"tool":"EMP","target":"silver, green, and orange cargo aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly extracts "EMP" ad verbatim instead of replacing it with "electromagnetic pulse".',
    },
    {
        "role": "user",
        "content": "Turret, lock onto target, unfriendly silver and yellow light aircraft, at three five two. Deploy electromagnetic pulse.",
    },
    {
        "role": "assistant",
        "content": '{"heading":352,"tool":"electromagnetic pulse","target":"silver and yellow light aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly extracts "electromagnetic pulse" ad verbatim instead of replacing it with "EMP".',
    },
    # Cases: ad verbatim.
    {
        "role": "user",
        "content": "Shoot green camouflage APC with torpedo system. Heading three one seven over.",
    },
    {
        "role": "assistant",
        "content": '{"heading":317,"tool":"torpedo","target":"green camouflage APC"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly extracts "APC" ad verbatim instead of replacing it with "armoured personnel carrier".',
    },
    {
        "role": "user",
        "content": "Team Alpha, use your LMG to shoot down hostile pink and purple drone cluster at one one three, over.",
    },
    {
        "role": "assistant",
        "content": '{"heading":113,"tool":"LMG","target":"pink and purple drone"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly extracts "LMG" ad verbatim instead of replacing it with "light machine gun".',
    },
    {
        "role": "user",
        "content": "Activate light machine gun system, target the dangerous green and red zombie cluster. Heading two zero zero. Engage at will.",
    },
    {
        "role": "assistant",
        "content": '{"heading":200,"tool":"light machine gun","target":"green and red zombie"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly extracts "light machine gun" ad verbatim instead of replacing it with "LMG".',
    },
    # Case: unnecessary suffix.
    {
        "role": "user",
        "content": "Activate machine gun system, target the hostile yellow, white, and orange fighter plane heading two niner five. Engage at will.",
    },
    {
        "role": "assistant",
        "content": '{"heading":295,"tool":"machine gun","target":"yellow, white, and orange fighter plane"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly discards the unnecessary suffix of "system".',
    },
    # Case: unnecessary suffix 2.
    {
        "role": "user",
        "content": "At one one nine engage red and blue drone cluster with drone catcher.",
    },
    {
        "role": "assistant",
        "content": '{"heading":119,"tool":"drone catcher","target":"red and blue drone"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly discards the unnecessary suffix of "cluster".',
    },
    # Case: unnecessary suffix 4.
    {
        "role": "user",
        "content": "Turret Foxtrot, heading zero niner eight, engage white, yellow, and orange light aircraft with machine gun fire.",
    },
    {
        "role": "assistant",
        "content": '{"heading":098,"tool":"machine gun","target":"white, yellow, and orange light aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly discards the unnecessary suffix of "fire".',
    },
    # Case: unnecessary prefix.
    {
        "role": "user",
        "content": "Control tower to interceptor jets, scramble immediately. We have an enemy blue, black, and silver cargo aircraft on heading three zero five. Engage and intercept the target. Over.",
    },
    {
        "role": "assistant",
        "content": '{"heading":305,"tool":"interceptor jets","target":"blue, black, and silver cargo aircraft"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly discards the unnecessary prefix of "enemy" which is not part of the target\'s appearance.',
    },
    # Case: plurality.
    {
        "role": "user",
        "content": "Block black, red, and purple missile at two four zero degrees with surface-to-air missiles.",
    },
    {
        "role": "assistant",
        "content": '{"heading":240,"tool":"surface-to-air missiles","target":"black, red, and purple missile"}',
    },
    {
        "role": "system",
        "content": 'Above answer correctly maintains the plurality of "surface-to-air missiles".',
    },
)
