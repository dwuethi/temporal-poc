FROM python:3.11-slim

WORKDIR /app

COPY shared ./shared
COPY client/client.py .

RUN pip install temporalio

CMD ["python", "client.py"]