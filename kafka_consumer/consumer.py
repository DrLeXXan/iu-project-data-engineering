import time
import json
import psycopg2
from kafka import KafkaConsumer

POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"
POSTGRES_DB = "factory_db"
POSTGRES_USER = "factory_user"
POSTGRES__PASSWORD = "mypassword"

KAFKA_BROKER = "kafka:9093"
KAFKA_TOPIC = ["factory_001","factory_002"]

BATCH_INTERVAL = 30


def get_postgres_connection():
        return psycopg2.connect(
              dbname=POSTGRES_DB,
              user=POSTGRES_USER,
              password=POSTGRES__PASSWORD,
              host=POSTGRES_HOST,
              port=POSTGRES_PORT
        )

def insert_messages(messages):
      if not messages:
            return

      conn = get_postgres_connection()
      cursor = conn.cursor()

      inster_query = "INSERT INTO factory.sensor_data (factory_id, engine_id, timestamp, temp_air, temp_oil, temp_exhaust, vibration, pressure_1, pressure_2, rpm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

      cursor.executemany(inster_query, messages)

      conn.commit()
      cursor.close()
      conn.close()


# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer(
      *KAFKA_TOPIC,
      group_id='my-group',
      bootstrap_servers=KAFKA_BROKER,
      value_deserializer=lambda x: json.loads(x.decode("utf-8"))
      )

buffer = []
start_time = time.time()

print("Listen for Kafka messages")


for message in consumer:
    # topic = message.topic
    data = json.loads(message.value)

    print(f"Received data {data}")

    buffer.append((data["factory_id"], data["engine_id"], data["timestamp"], data["temp_air"], data["temp_oil"], data["temp_exhaust"], data["vibration"], data["pressure_1"], data["pressure_2"], data["rpm"]))


    if time.time() - start_time >= BATCH_INTERVAL:
          insert_messages(buffer)

          buffer.clear()
          start_time = time.time()
