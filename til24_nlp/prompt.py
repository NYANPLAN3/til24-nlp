"""Model prompt."""

__all__ = ["SYS_PROMPT", "EXAMPLES"]

# TODO: Consider CoT or other pre-prompt techniques? Effect on speed...
# NOTE: JSON schema tends to confuse models unless you give examples. Perhaps, giving
# solely examples is better.
SYS_PROMPT = (
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

EXAMPLES = (
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
)
