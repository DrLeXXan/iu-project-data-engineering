FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

COPY cryptography_service.py .

EXPOSE 8000

CMD ["uvicorn", "cryptography_service:app", "--host", "0.0.0.0", "--port", "8000"]
