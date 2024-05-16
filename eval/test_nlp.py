"""Taken from https://github.com/TIL-24/til-24-base/blob/main/test_nlp.py."""

import json
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

from eval.nlp_eval import nlp_eval

load_dotenv()

TEAM_NAME = os.getenv("TEAM_NAME")
TEAM_TRACK = os.getenv("TEAM_TRACK")
HOME = os.getenv("HOME")


def main():
    input_dir = Path(f"{HOME}/{TEAM_TRACK}")
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    with open(input_dir / "nlp.jsonl", "r") as f:
        instances = [json.loads(line.strip()) for line in f if line.strip() != ""]

    results = run_batched(instances)
    df = pd.DataFrame(results)
    df.to_csv(results_dir / "nlp_results.csv", index=False)
    # calculate eval
    eval_result = nlp_eval(
        [result["truth"] for result in results],
        [result["prediction"] for result in results],
    )
    print(f"NLP result: {eval_result}")
    wrong_arr = []
    for result in results:
        for k, v1 in result["truth"].items():
            v2 = result["prediction"][k]
            if v1 != v2:
                wrong_arr.append(
                    dict(
                        key=result["key"],
                        transcript=result["transcript"],
                        field=k,
                        truth=v1,
                        prediction=v2,
                    )
                )
    wrong_df = pd.DataFrame(wrong_arr)
    wrong_df.to_csv(results_dir / "nlp_wrong.csv", index=False)


def run_batched(
    instances: List[Dict[str, str | int]], batch_size: int = 64
) -> List[Dict[str, str | int]]:
    # split into batches
    results = []
    # for index in tqdm(range(0, 256, batch_size)):
    for index in tqdm(range(0, len(instances), batch_size)):
        _instances = instances[index : index + batch_size]
        response = requests.post(
            "http://localhost:5002/extract",
            data=json.dumps(
                {
                    "instances": [
                        {"key": _instance["key"], "transcript": _instance["transcript"]}
                        for _instance in _instances
                    ]
                }
            ),
        )
        _results = response.json()["predictions"]
        results.extend(
            [
                {
                    "key": _instances[i]["key"],
                    "transcript": _instances[i]["transcript"],
                    "truth": {
                        field: _instances[i][field]
                        for field in ("heading", "target", "tool")
                    },
                    "prediction": _results[i],
                }
                for i in range(len(_instances))
            ]
        )
    return results


if __name__ == "__main__":
    main()
