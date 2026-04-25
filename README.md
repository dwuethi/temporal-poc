# Temporal PoC

## What it does

This PoC demonstrates a Temporal workflow that:

1. Reads an input file
2. Calls an external REST API
3. Writes the processed result to disk

---

## Requirements

- Docker Desktop (running)

---

## Start services

```bash
docker-compose up --build
```

---

## Stop services

```bash
docker-compose down
```

---

## Run workflow

```bash
docker-compose run --rm client python client.py
```

Starts a one-off client container that triggers a workflow execution.

---

## Temporal UI

http://localhost:8233

---

## Rebuild (if needed)

```bash
docker-compose build --no-cache
```

---

## Logs

```bash
docker-compose logs -f
```

---

## Project Structure

```text
client/     → starts workflow execution
worker/     → workflow + activities (Temporal worker)
shared/     → workflow definitions
data/       → input/output files
```

---
