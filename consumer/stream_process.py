from bytewax.connectors.kafka import KafkaSource
from bytewax import operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink
import time

print("Wait for Kafka Topic")
time.sleep(10)
print("Start Bytewax")

KAFKA_BROKER = ["kafka:9093"]
KAFKA_TOPIC = ["factory_001"]

flow = Dataflow("Kafka-Test")
kinp = op.input("kafka-in", flow, KafkaSource(KAFKA_BROKER, KAFKA_TOPIC))

op.output("out", kinp, StdOutSink())
