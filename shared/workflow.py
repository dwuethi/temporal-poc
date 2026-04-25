from datetime import timedelta
from temporalio import workflow


@workflow.defn
class FileWorkflow:
    @workflow.run
    async def run(self, workflow_id: str) -> str:
        base_path = f"/data/workspaces/{workflow_id}"

        text = await workflow.execute_activity(
            "read_file",
            f"{base_path}/input.txt",
            start_to_close_timeout=timedelta(seconds=10),
        )

        processed = await workflow.execute_activity(
            "call_rest",
            text,
            start_to_close_timeout=timedelta(seconds=20),
        )

        await workflow.execute_activity(
            "write_file",
            {"path": f"{base_path}/output.txt", "content": processed},
            start_to_close_timeout=timedelta(seconds=10),
        )

        return "DONE"