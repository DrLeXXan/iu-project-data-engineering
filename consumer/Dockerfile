# Start from a debian slim with python support
FROM python:3.11-slim

# Set up a workdir where we can put our dataflow
WORKDIR /bytewax

# Install system dependencies required for Bytewax, Kafka, and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    librdkafka-dev \
    rustc \
    cargo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip, install maturin manually, and ensure we have wheel
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir maturin setuptools wheel

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY stream_process.py stream_process.py

# Set PYTHONUNBUFFERED to any value to make python flush stdout
ENV PYTHONUNBUFFERED 1

CMD ["python", "-m", "bytewax.run", "stream_process"]
