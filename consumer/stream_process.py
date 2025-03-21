import json
import time
from datetime import datetime, timedelta, timezone

from bytewax.connectors.kafka import KafkaSource
from bytewax import operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink

from bytewax.operators.windowing import (
    EventClock,
    TumblingWindower,
    reduce_window,
)


time.sleep(10)


# Define the Bytewax dataflow
flow = Dataflow("Exmaple-Flow")

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

        return message_dict

    except Exception as e:
        print(f"Error parsing Kafka message: {e}")
        return None  # Return None if there's an error

def extract_timestamp(msg):
    """Extract and convert Kafka timestamp"""
    return datetime.strptime(msg["timestamp"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

kinp = op.input("kafka-in", flow, kafka_source)

mapped = op.map("extract_string", kinp, lambda x: extract_value(x))

keyed_stream = op.key_on("key_on_engine_id", mapped, lambda e: e["engine_id"])

clock = EventClock(
    ts_getter=extract_timestamp,
    wait_for_system_duration=timedelta(seconds=10)
)
windower = TumblingWindower(
    length=timedelta(seconds=10),
    align_to=datetime(2024, 8, 29, 8, 0, 0, tzinfo=timezone.utc)
)

def add(acc, x):
    acc["temp_air"] += x["temp_air"]
    return acc

windowed_avg = reduce_window(
    step_id="average_temp_air",
    up=keyed_stream,
    clock=clock,
    windower=windower,
    reducer=add
)

op.output("out", windowed_avg.down, StdOutSink())
