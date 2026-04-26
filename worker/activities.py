import os
import subprocess 

import boto3
from botocore.config import Config
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

@activity.defn
def run_cli(input_text: str) -> str:
    result = subprocess.run(
        ["tr", "a-z", "A-Z"],
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _s3_client(endpoint_url: str | None = None):
    kwargs = {
        "config": Config(s3={"addressing_style": "path"}),
    }
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("s3", **kwargs)


@activity.defn
def download_s3_object(data: dict) -> str:
    os.makedirs(os.path.dirname(data["path"]), exist_ok=True)
    _s3_client(data.get("endpoint_url")).download_file(
        data["bucket"],
        data["key"],
        data["path"],
    )
    return data["path"]


@activity.defn
def run_ilivalidator(data: dict) -> dict:
    log_path = data["log_path"]
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    command = [
        "java",
        "-jar",
        os.environ.get("ILIVALIDATOR_JAR", "/opt/ilivalidator/ilivalidator.jar"),
        *data.get("args", []),
        "--log",
        log_path,
        data["input_path"],
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n")
                f.write(result.stderr)

    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "log_path": log_path,
    }


@activity.defn
def upload_s3_object(data: dict) -> str:
    extra_args = {}
    if data.get("content_type"):
        extra_args["ContentType"] = data["content_type"]

    _s3_client(data.get("endpoint_url")).upload_file(
        data["path"],
        data["bucket"],
        data["key"],
        ExtraArgs=extra_args or None,
    )
    return f"s3://{data['bucket']}/{data['key']}"
