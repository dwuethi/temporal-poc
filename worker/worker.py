import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from shared.workflow import FileWorkflow
from activities import read_file, write_file, call_rest, run_cli


async def wait_for_temporal() -> Client:
    while True:
        try:
            client = await Client.connect(
                "temporal:7233",
                namespace="default",
            )

            async for _ in client.list_workflows(page_size=1):
                break

            print("Temporal ready (worker)!")
            return client

        except Exception as e:
            print("Waiting for Temporal (worker)...", e)
            await asyncio.sleep(2)


async def main():
    client = await wait_for_temporal()

    worker = Worker(
        client,
        task_queue="queue",
        workflows=[FileWorkflow],
        activities=[read_file, write_file, call_rest, run_cli],
        activity_executor=ThreadPoolExecutor(max_workers=10),
    )

    print("Worker started!")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())