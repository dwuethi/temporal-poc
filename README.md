# Temporal PoC

This project is a local Temporal proof of concept with two independent workflows:

1. A simple file-processing workflow.
2. An INTERLIS `ilivalidator` workflow that uses local MinIO as S3 storage.

Everything runs locally through Docker Compose.

---

## Services

- `temporal`: Temporal server
- `temporal-ui`: Temporal Web UI
- `postgres`: Temporal persistence database
- `minio`: local S3-compatible object storage
- `minio-init`: creates local buckets and uploads the RoadsSimple sample files
- `worker`: worker for the simple file workflow
- `ilivalidator-worker`: worker for the S3 ilivalidator workflow
- `client`: one-off container used to start workflow executions

---

## Start

```bash
docker-compose up --build
```

This starts Temporal, MinIO, both workers, and prepares MinIO with:

- bucket `interlis-input`
- bucket `interlis-output`
- object `interlis-input/RoadsSimple.xtf`
- object `interlis-input/RoadsSimple.ili`

The RoadsSimple files are stored locally in:

```text
data/samples/RoadsSimple.xtf
data/samples/RoadsSimple.ili
```

---

## UIs

Temporal UI:

```text
http://localhost:8233
```

MinIO Console:

```text
http://localhost:9001
```

MinIO login:

- User: `minioadmin`
- Password: `minioadmin`

---

## Workflow 1: File Processing

This is the original demo workflow.

What it does:

1. The client creates a workflow workspace under `/data/workspaces/<workflow-id>`.
2. The client writes `input.txt`.
3. The workflow reads the file.
4. The worker runs a local CLI step that uppercases the text.
5. The worker calls a test REST endpoint.
6. The worker writes `output.txt`.

Run it:

```bash
docker-compose run --rm client python client.py
```

The output is written under:

```text
data/workspaces/<workflow-id>/output.txt
```

---

## Workflow 2: S3 ilivalidator

This workflow validates an INTERLIS transfer file with `ilivalidator`.

What it does:

1. `minio-init` creates the local MinIO buckets.
2. `minio-init` uploads `RoadsSimple.xtf` and `RoadsSimple.ili` to `interlis-input`.
3. The workflow downloads `RoadsSimple.xtf` from MinIO.
4. The workflow also downloads `RoadsSimple.ili` as a companion model file.
5. The worker runs `java -jar ilivalidator.jar --log ... RoadsSimple.xtf`.
6. The workflow uploads the validator log to `interlis-output`.

Run it:

```bash
docker-compose run --rm client python ilivalidator_client.py
```

Default input:

```text
s3://interlis-input/RoadsSimple.xtf
s3://interlis-input/RoadsSimple.ili
```

Default output:

```text
s3://interlis-output/RoadsSimple.xtf.ilivalidator.log
```

Download the validator log into `data/RoadsSimple.ilivalidator.log`:

```bash
docker-compose run --rm --entrypoint sh minio-client -c "mc alias set local http://minio:9000 minioadmin minioadmin && mc cp local/interlis-output/RoadsSimple.xtf.ilivalidator.log /data/RoadsSimple.ilivalidator.log"
```

You can also inspect the input and output buckets in the MinIO Console.

---

## Stop

```bash
docker-compose down
```

Remove MinIO data too:

```bash
docker-compose down -v
```

---

## Rebuild

```bash
docker-compose build --no-cache
```

---

## Logs

```bash
docker-compose logs -f
```

Specific worker logs:

```bash
docker-compose logs -f ilivalidator-worker
```

---

## Project Structure

```text
client/     -> starts workflow executions
worker/     -> Temporal workers and activities
shared/     -> workflow definitions
data/       -> local samples and workflow outputs
```
