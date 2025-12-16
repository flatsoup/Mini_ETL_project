FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY config.yaml ./config.yaml
COPY data ./data

RUN mkdir -p logs data/raw data/processed data/warehouse

CMD ["python", "-m", "src.etl.main", "--config", "config.yaml"]