FROM flink:1.16

# install python3: it has updated Python to 3.9 in Debian 11 and so install Python 3.7 from source, \
# it currently only supports Python 3.6, 3.7 and 3.8 in PyFlink officially.

RUN apt-get update -y && \
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev && \
wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
tar -xvf Python-3.7.9.tgz && \
cd Python-3.7.9 && \
./configure --without-tests --enable-shared && \
make -j6 && \
make install && \
ldconfig /usr/local/lib && \
cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
ln -s /usr/local/bin/python3 /usr/local/bin/python && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# install PyFlink
RUN pip3 install "apache-flink>=1.16.0,<1.17.1"

# add python script
USER flink
RUN mkdir /opt/flink/usrlib
ADD stream_process.py /opt/flink/usrlib/python_demo.py

# FROM flink:latest

# # install python3 and pip3
# RUN apt-get update -y && \
# apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
# RUN ln -s /usr/bin/python3 /usr/bin/python

# # install PyFlink

# COPY apache_flink*.tar.gz /
# RUN pip3 install /apache_flink_libraries*.tar.gz && pip3 install /apache_flink*.tar.gz

# FROM flink:1.17.1


# RUN apt-get update -y && \
# apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
# RUN ln -s /usr/bin/python3 /usr/bin/python

# COPY apache_flink*.tar.gz /
# RUN pip3 install /apache_flink_libraries*.tar.gz && pip3 install /apache_flink*.tar.gz
# # Install PyFlink and dependencies
# RUN pip3 install apache-flink

# RUN wget -q https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.17.1/flink-connector-kafka-1.17.1.jar -P /opt/flink/lib/
# RUN wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar -P /opt/flink/lib/


# # Copy the Flink Python script
# COPY stream_process.py /opt/flink/stream_process.py

# # Run Flink job on container start
# CMD ["python3", "/opt/flink/stream_process.py"]
