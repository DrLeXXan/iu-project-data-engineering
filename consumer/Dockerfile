FROM flink:2.0-java17

WORKDIR /opt/flink

RUN wget -q https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.17.0/flink-connector-kafka-1.17.0.jar -P /opt/flink/lib/

RUN apt-get update && apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt /opt/flink/requirements.txt

RUN set -ex; \
    pip install --no-cache-dir -r /opt/flink/requirements.txt

COPY stream_process.py /opt/flink/stream_process.py

# Set Python path explicitly
ENV PYTHON_EXEC=/usr/bin/python3
ENV PYTHONHOME=/usr
ENV PYTHONPATH=/usr/lib/python3.8


EXPOSE 8081 6123 6124

CMD ["sh", "-c", "jobmanager & python3 /opt/flink/stream_process.py"]
