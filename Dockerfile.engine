# FROM python:3.9

# WORKDIR /app

# COPY IoT_engine.py /app

# RUN pip install cryptography fastapi uvicorn

# EXPOSE 8000

# # CMD [ "python", "-u", "IoT_engine.py" ]

# Use Python official image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy files
COPY IoT_engine.py .

# Install FastAPI and Uvicorn
RUN pip install cryptography fastapi uvicorn

# Expose the FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "IoT_engine:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
