FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /app/input /app/output

COPY runner.py /app/runner.py

ENTRYPOINT ["python", "runner.py"]
