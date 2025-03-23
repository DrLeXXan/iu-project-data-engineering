import json
import time
from datetime import datetime, timedelta, timezone

import psycopg2

from bytewax.connectors.kafka import KafkaSource
from bytewax import operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink
from bytewax.operators.windowing import (
    EventClock,
    TumblingWindower,
    collect_window,
)

# Delay to make sure Kafka is running and topic is created
time.sleep(10)


DB_CONFIG = {
    "dbname" : "factory_db",
    "user" : "factory_user",
    "password" : "mypassword",
    "host" : "postgres",
    "port" : "5432",
}

# Kafka Source (consume messages from topic)
kafka_source = KafkaSource(
    brokers=["kafka:9093"],
    topics=["factory_001"],
)


def extract_value(msg):
    """Extract JSON data from KafkaSourceMessage."""
    try:
        # Decode byte string to a normal string
        message_str = msg.value.decode("utf-8")

        # Convert JSON string to Python dictionary
        message_dict = json.loads(json.loads(message_str))

        print(f"Kafka Timestamp: {msg.timestamp}")

        return message_dict

    except Exception as e:
        print(f"Error parsing Kafka message: {e}")
        return None  # Return None if there's an error


def extract_timestamp(msg):
    """Extract and convert Kafka timestamp"""
    timestamp = datetime.strptime(msg["timestamp"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    print(f"Timestamp_def: {timestamp}")
    return datetime.strptime(msg["timestamp"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)


def PostgresSink(data):
      conn = psycopg2.connect(**DB_CONFIG)
      cursor = conn.cursor()

      cursor.execute("""
                INSERT INTO factory.sensor_data
                (factory_id, engine_id, timestamp, temp_air, temp_oil, temp_exhaust, vibration, pressure_1, pressure_2, rpm)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                data["factory_id"],
                data["engine_id"],
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
                data["temp_air"],
                data["temp_oil"],
                data["temp_exhaust"],
                data["vibration"],
                data["pressure_1"],
                data["pressure_2"],
                data["rpm"]
            ))

      conn.commit()
      cursor.close()
      conn.close()



def PostgresAvgSink(batch):

    print(f"Data: {batch}")
    # -- Aggregate the collected data --

    data = batch[1][1]
    # print(f"data: {data}")
    factory_id = data[0]["factory_id"]
    # print(f"data: {factory_id}")
    engine_id = batch[0]
    # print(f"data: {engine_id}")
    epoch_time = batch[1][0]
    print(f"data: {epoch_time}")
    utc_datetime = datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"UTC: {utc_datetime}")
    print(f"Without: {datetime.fromtimestamp(epoch_time)}")

    for row in data:
        temp_air = temp_oil = temp_exhaust = vibration = pressure_1 = pressure_2 = rpm = 0.00
        count = 0

        temp_air += row["temp_air"]
        temp_oil += row["temp_oil"]
        temp_exhaust += row["temp_exhaust"]
        vibration += row["vibration"]
        pressure_1 += row["pressure_1"]
        pressure_2 += row["pressure_2"]
        rpm += row["rpm"]

        count += 1


    avg_temp_air = temp_air / count
    avg_temp_oil = temp_oil / count
    avg_temp_exhaust = temp_exhaust / count
    avg_vibration = vibration / count
    avg_pressure_1 = pressure_1 / count
    avg_pressure_2 = pressure_2 / count
    avg_rpm = rpm / count


    # print(f"Avg: {factory_id,engine_id,utc_datetime,avg_temp_air,avg_temp_oil,avg_temp_exhaust,avg_vibration,avg_pressure_1,avg_pressure_2,avg_rpm, count}")


    # -- Save aggreagted value into PostgresDB --

    conn = psycopg2.connect(**DB_CONFIG)
    # print("Database connected successfully")
    cursor = conn.cursor()

    cursor.execute("""
                INSERT INTO factory.aggregated_sensor_data
                (factory_id, engine_id, watermark, avg_temp_air, avg_temp_oil, avg_temp_exhaust, avg_vibration, avg_pressure_1, avg_pressure_2, avg_rpm, batch_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                factory_id,
                engine_id,
                utc_datetime,
                avg_temp_air,
                avg_temp_oil,
                avg_temp_exhaust,
                avg_vibration,
                avg_pressure_1,
                avg_pressure_2,
                avg_rpm,
                count
            ))


    conn.commit()
    cursor.close()
    conn.close()


# Define the Bytewax dataflow
flow = Dataflow("Exmaple-Flow")

kinp = op.input("kafka-in", flow, kafka_source)

mapped = op.map("extract_string", kinp, lambda x: extract_value(x))

op.map("raw_to_postgres", mapped, lambda x: PostgresSink(x))



keyed_stream = op.key_on("key_on_engine_id", mapped, lambda e: e["engine_id"])

clock = EventClock(
    ts_getter=extract_timestamp,
    wait_for_system_duration=timedelta(seconds=10)
)
windower = TumblingWindower(
    length=timedelta(seconds=10),
    align_to=datetime(2025, 1, 1, tzinfo=timezone.utc)
)

windowed = collect_window(
    step_id="collect_window",
    up=keyed_stream,
    clock=clock,
    windower=windower,
)

op.output("output-window", windowed.down, StdOutSink())

op.map("avg_to_postgres", windowed.down, lambda x: PostgresAvgSink(x))

# op.output("output", mapped, StdOutSink())
