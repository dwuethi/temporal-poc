import os

import requests
from temporalio import activity


@activity.defn
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@activity.defn
def call_rest(data: str) -> str:
    response = requests.post(
        "https://httpbin.org/post",
        json={"input": data},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["json"]["input"] + " processed"


@activity.defn
def write_file(data: dict) -> str:
    with open(data["path"], "w", encoding="utf-8") as f:
        f.write(data["content"])
    return data["path"]