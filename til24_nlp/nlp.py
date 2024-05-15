"""does nlp."""

import logging
import time

import instructor
from openai import OpenAI
from pydantic import BaseModel

log = logging.getLogger(__name__)


class Character(BaseModel):
    """ddd."""

    tool: str
    target: str
    heading: int


client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:5002/llama-cpp-python/v1",
        api_key="localhost",
    ),
    mode=instructor.Mode.JSON,
)


def nlp_magic(sentence: str):
    # enables `response_model` in create call
    # initialised

    starttime = time.time()
    try:
        resp = client.chat.completions.create(
            model="phi3",
            messages=[
                {
                    "role": "system",
                    "content": """tyou are used for function calling to catergorize a natural language prompt into the form
                    tool: str,
                    heading: int,
                    target: str
                    headings are integers. if a number is given, turn it into an integer
                    """,
                },
                {
                    "role": "user",
                    "content": sentence,
                },
            ],
            response_model=Character,
            max_retries=1,
        )
    except Exception as e:
        log.error(f'"{sentence}" failed.', exc_info=e)
        return Character(tool="", target="", heading=0)

    endtime = time.time()
    time_taken = endtime - starttime
    log.info(f"Time taken: {time_taken} seconds")

    return resp


if __name__ == "__main__":
    sentence = (
        "Bravo, engage with machine gun, heading two three zero, target black drone."
    )
    ouput = nlp_magic(sentence)

    print(ouput)
