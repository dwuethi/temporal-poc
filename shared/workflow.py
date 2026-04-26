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

        processed_cli = await workflow.execute_activity(
            "run_cli",
            text,
            start_to_close_timeout=timedelta(seconds=10),
        )

        enriched = await workflow.execute_activity(
            "call_rest",
            processed_cli,
            start_to_close_timeout=timedelta(seconds=20),
        )

        await workflow.execute_activity(
            "write_file",
            {
                "path": f"{base_path}/output.txt",
                "content": enriched,
            },
            start_to_close_timeout=timedelta(seconds=10),
        )

        return "DONE"


@workflow.defn
class IlivalidatorS3Workflow:
    @workflow.run
    async def run(self, request: dict) -> dict:
        workflow_id = workflow.info().workflow_id
        workspace = request.get("workspace", f"/data/workspaces/{workflow_id}")
        input_name = request.get("input_name", request["source_key"].split("/")[-1])
        input_path = f"{workspace}/{input_name}"
        log_path = request.get("log_path", f"{workspace}/ilivalidator.log")

        await workflow.execute_activity(
            "download_s3_object",
            {
                "bucket": request["source_bucket"],
                "key": request["source_key"],
                "path": input_path,
                "endpoint_url": request.get("endpoint_url"),
            },
            start_to_close_timeout=timedelta(minutes=10),
        )

        for companion_key in request.get("companion_keys", []):
            await workflow.execute_activity(
                "download_s3_object",
                {
                    "bucket": request["source_bucket"],
                    "key": companion_key,
                    "path": f"{workspace}/{companion_key.split('/')[-1]}",
                    "endpoint_url": request.get("endpoint_url"),
                },
                start_to_close_timeout=timedelta(minutes=10),
            )

        validation = await workflow.execute_activity(
            "run_ilivalidator",
            {
                "input_path": input_path,
                "log_path": log_path,
                "args": request.get("validator_args", []),
            },
            start_to_close_timeout=timedelta(minutes=30),
        )

        await workflow.execute_activity(
            "upload_s3_object",
            {
                "bucket": request["target_bucket"],
                "key": request["target_key"],
                "path": log_path,
                "endpoint_url": request.get("endpoint_url"),
                "content_type": "text/plain",
            },
            start_to_close_timeout=timedelta(minutes=10),
        )

        return {
            "status": "VALID" if validation["exit_code"] == 0 else "INVALID",
            "exit_code": validation["exit_code"],
            "source": f"s3://{request['source_bucket']}/{request['source_key']}",
            "report": f"s3://{request['target_bucket']}/{request['target_key']}",
            "stdout": validation["stdout"],
            "stderr": validation["stderr"],
        }
