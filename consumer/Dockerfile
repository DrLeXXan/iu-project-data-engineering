# Start from a debian slim with python support
FROM python:3.11-slim-bullseye
# Set up a workdir where we can put our dataflow
WORKDIR /bytewax
# Install bytewax and the dependencies you need here
RUN pip install bytewax==0.21.1
RUN pip install confluent_kafka
RUN pip install orjson
RUN pip install typing
RUN pip install datetime

# Copy the dataflow in the workdir
COPY stream_process.py stream_process.py
# And run it.
# Set PYTHONUNBUFFERED to any value to make python flush stdout,
# or you risk not seeing any output from your python scripts.
ENV PYTHONUNBUFFERED 1
CMD ["python", "-m", "bytewax.run", "stream_process"]
