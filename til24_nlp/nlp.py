"""does nlp."""

import logging
import time

import instructor
from openai import OpenAI
from pydantic import BaseModel

log = logging.getLogger(__name__)


class Character(BaseModel):

    tool: str
    target: str
    heading: int


client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
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
                    "content": """
                    given a transcript, you will extract these 3 things: 

                    1.tools are weapons. some tools are electromagnetic pulse, surface-to-air missiles, EMP, machine gun, anti-air artillery, interceptor jets, 
                    drone catcher. if none found, infer from the sentence.

                    2.targets are objects with description.

                    3.headings integers compass direction. if there is more than one number,only return the one that 
                    describes direction.
                    """,
                },
                {
                    "role": "user",
                    "content": sentence,
                },
            ],
            response_model=Character,
        )
    except Exception:
        log.error(f'"{sentence}" failed.')
        return Character(tool="", target="", heading=0)
    


    endtime = time.time()
    time_taken = endtime - starttime
    log.info(f"Time taken: {time_taken} seconds")

    return resp


if __name__ == "__main__":
    import pandas as pd
    import csv


    df = pd.read_csv('data.csv')
    transcript_list = df['transcript'].tolist()

    

    output_list = []
    failed_list = []
    counter=1
    list_size = len(transcript_list)
    for transcript in transcript_list:
        ouput = nlp_magic(transcript).model_dump()
        print(f"{ouput}........{counter}/{list_size} Done")
        output_list.append(ouput)
        counter += 1
        


        if ouput == {'tool': '', 'target': '', 'heading': 0}:
            failed_list.append(transcript)
            with open("mycsvfile.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(failed_list)