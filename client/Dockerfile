FROM python:3.11-slim

WORKDIR /app

COPY shared ./shared
COPY client .

RUN pip install temporalio

CMD ["python", "client.py"]
