FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

COPY verification_service.py .

CMD ["python", "-u", "verification_service.py"]
