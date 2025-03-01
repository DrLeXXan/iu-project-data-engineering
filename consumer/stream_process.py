from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.connectors.jdbc import JdbcSink, JdbcConnectionOptions, JdbcExecutionOptions
from pyflink.common.serialization import SimpleStringSchema
import json

# Initialize Flink environment
env = StreamExecutionEnvironment.get_execution_environment()

# Kafka consumer setup
kafka_consumer = FlinkKafkaConsumer(
    topics='factory_001',
    deserialization_schema=SimpleStringSchema(),
    properties={'bootstrap.servers': 'kafka:9093', 'group.id': 'flink-group'}
)

# Define data stream
stream = env.add_source(kafka_consumer)

# Parse JSON messages
def parse_message(message):
    try:
        data = json.loads(message)
        return (data['factory_id'], data['engine_id'], data['timestamp'])
    except:
        return None

parsed_stream = stream.map(parse_message).filter(lambda x: x is not None)

# PostgreSQL sink
jdbc_sink = JdbcSink.sink(
    "INSERT INTO messages (factory_id, engine_id, timestamp) VALUES (?, ?, ?)",
    lambda stmt, record: (stmt.setInt(1, record[0]), stmt.setString(2, record[1]), stmt.setString(3, record[2])),
    JdbcExecutionOptions.builder()
        .with_batch_interval_ms(200)
        .with_batch_size(100)
        .with_max_retries(3)
        .build(),
    JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
        .with_url("jdbc:postgresql://postgres:5432/factory_db")
        .with_driver_name("org.postgresql.Driver")
        .with_user_name("flink_user")
        .with_password("mypassword")
        .build()
)

# Add sink to stream
parsed_stream.add_sink(jdbc_sink)

# Execute the Flink job
env.execute("Kafka to PostgreSQL Streaming Job")
