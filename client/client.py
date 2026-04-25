import asyncio
import os
import uuid
from datetime import timedelta

from temporalio.client import Client

from shared.workflow import FileWorkflow


async def wait_for_temporal() -> Client:
    while True:
        try:
            client = await Client.connect(
                "temporal:7233",
                namespace="default",
            )

            async for _ in client.list_workflows(page_size=1):
                break

            print("Temporal ready (client)!")
            return client

        except Exception as e:
            print("Waiting for Temporal (client)...", e)
            await asyncio.sleep(2)


async def main():
    client = await wait_for_temporal()

    workflow_id = f"wf-{uuid.uuid4()}"
    base = f"/data/workspaces/{workflow_id}"
    os.makedirs(base, exist_ok=True)

    with open(f"{base}/input.txt", "w", encoding="utf-8") as f:
        f.write("hello geopilot")

    result = await client.execute_workflow(
        FileWorkflow.run,
        workflow_id,
        id=workflow_id,
        task_queue="queue",
        execution_timeout=timedelta(minutes=1),
    )

    print("Workflow ID:", workflow_id)
    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())