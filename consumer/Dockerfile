FROM python:3.11-slim

WORKDIR /bytewax

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    librdkafka-dev \
    rustc \
    cargo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir maturin setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stream_process.py stream_process.py

# Set PYTHONUNBUFFERED to any value to make python flush stdout
ENV PYTHONUNBUFFERED 1

CMD ["python", "-m", "bytewax.run", "stream_process"]
