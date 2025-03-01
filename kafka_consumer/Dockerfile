FROM python:3.9-alpine

WORKDIR /app

RUN apk update && apk add --no-cache \
    postgresql-libs \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    && pip install --no-cache-dir --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY consumer.py .

CMD ["python", "consumer.py"]
