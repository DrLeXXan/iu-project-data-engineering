FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

COPY api-server.py api-server.py
COPY frontend/ frontend/

CMD ["uvicorn", "api-server:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
