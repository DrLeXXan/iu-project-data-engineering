FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

COPY factory.py .

CMD ["uvicorn", "factory:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
