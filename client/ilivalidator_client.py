import asyncio
import os
import uuid
from datetime import timedelta

from temporalio.client import Client

from shared.workflow import IlivalidatorS3Workflow


async def wait_for_temporal() -> Client:
    while True:
        try:
            client = await Client.connect(
                "temporal:7233",
                namespace="default",
            )

            async for _ in client.list_workflows(page_size=1):
                break

            print("Temporal ready (ilivalidator client)!")
            return client

        except Exception as e:
            print("Waiting for Temporal (ilivalidator client)...", e)
            await asyncio.sleep(2)


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main():
    client = await wait_for_temporal()

    workflow_id = os.environ.get("WORKFLOW_ID", f"ilivalidator-{uuid.uuid4()}")
    source_bucket = os.environ.get("S3_SOURCE_BUCKET", "interlis-input")
    source_key = os.environ.get("S3_SOURCE_KEY", "RoadsSimple.xtf")
    target_bucket = os.environ.get("S3_TARGET_BUCKET", "interlis-output")
    target_key = os.environ.get("S3_TARGET_KEY", f"{source_key}.ilivalidator.log")

    request = {
        "source_bucket": source_bucket,
        "source_key": source_key,
        "companion_keys": [
            key.strip()
            for key in os.environ.get("S3_COMPANION_KEYS", "RoadsSimple.ili").split(",")
            if key.strip()
        ],
        "target_bucket": target_bucket,
        "target_key": target_key,
        "endpoint_url": os.environ.get("S3_ENDPOINT_URL", "http://minio:9000"),
    }

    result = await client.execute_workflow(
        IlivalidatorS3Workflow.run,
        request,
        id=workflow_id,
        task_queue="ilivalidator-queue",
        execution_timeout=timedelta(hours=1),
    )

    print("Workflow ID:", workflow_id)
    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())
