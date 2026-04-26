import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from activities import download_s3_object, run_ilivalidator, upload_s3_object
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

            print("Temporal ready (ilivalidator worker)!")
            return client

        except Exception as e:
            print("Waiting for Temporal (ilivalidator worker)...", e)
            await asyncio.sleep(2)


async def main():
    client = await wait_for_temporal()

    worker = Worker(
        client,
        task_queue="ilivalidator-queue",
        workflows=[IlivalidatorS3Workflow],
        activities=[download_s3_object, run_ilivalidator, upload_s3_object],
        activity_executor=ThreadPoolExecutor(max_workers=10),
    )

    print("Ilivalidator worker started!")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
