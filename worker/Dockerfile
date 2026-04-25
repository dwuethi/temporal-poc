FROM python:3.11-slim

WORKDIR /app

COPY shared ./shared
COPY worker .

RUN pip install -r requirements.txt

CMD ["python", "worker.py"]