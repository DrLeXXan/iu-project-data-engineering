from datetime import datetime
from typing import Iterable
import json

from pyflink.common import Time, WatermarkStrategy, Duration, Row
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext, WindowFunction, ProcessFunction
from pyflink.datastream.state import ValueStateDescriptor, StateTtlConfig
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.window import TumblingEventTimeWindows, TimeWindow



# Kafka consumer settings
KAFKA_BROKER = "kafka:9093"
KAFKA_TOPIC = "factory_001"

def show(ds, env):
    ds.print()
    env.execute()

# class Sum(KeyedProcessFunction):

#     def __init__(self):
#         self.state = None

#     def open(self, runtime_context: RuntimeContext):
#         state_descriptor = ValueStateDescriptor("state", Types.FLOAT())
#         state_ttl_config = StateTtlConfig \
#             .new_builder(Time.seconds(1)) \
#             .set_update_type(StateTtlConfig.UpdateType.OnReadAndWrite) \
#             .disable_cleanup_in_background() \
#             .build()
#         state_descriptor.enable_time_to_live(state_ttl_config)
#         self.state = runtime_context.get_state(state_descriptor)

#     def process_element(self, value, ctx: 'KeyedProcessFunction.Context'):
#         # retrieve the current count
#         current = self.state.value()
#         if current is None:
#             current = 0

#         # update the state's count
#         current += value[1]
#         self.state.update(current)

#         # register an event time timer 5 seconds later
#         ctx.timer_service().register_event_time_timer(ctx.timestamp() + 5000)

#     def on_timer(self, timestamp: int, ctx: 'KeyedProcessFunction.OnTimerContext'):
#         print(ctx.get_current_key(), self.state.value())
#         yield ctx.get_current_key(), self.state.value()


class Sum(KeyedProcessFunction):

    def __init__(self):
        self.state = None

    def open(self, runtime_context: RuntimeContext):
        self.state = runtime_context.get_state(ValueStateDescriptor(
            "my_state", Types.PICKLED_BYTE_ARRAY()))

    def process_element(self, value, ctx: 'ProcessFunction.Context'):
        # retrieve the current count
        current = self.state.value()

        if current is None:
            current = [0, 0]

        # update the state's count
        current[0] += value[2]

        # update the state's count
        # current[1] += 1

        current[1] = ctx.timestamp()

        self.state.update(current)

        print(f"Value, Current: {value, current}")

        # write the state back
        self.state.update(current)

        # schedule the next timer 60 seconds from the current event time
        ctx.timer_service().register_event_time_timer(current[1] + 5000)


    def on_timer(self, timestamp: int, ctx: 'KeyedProcessFunction.OnTimerContext'):
        print(f"Result after 5 secons: {ctx.get_current_key(), self.state.value()}")
        yield ctx.get_current_key(), self.state.value()


class MyTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp) -> int:
        # Convert 'YYYY-MM-DD HH:MM:SS' to milliseconds since epoch
        event_time = datetime.strptime(value[1], "%Y-%m-%d %H:%M:%S")
        return int(event_time.timestamp() * 1000)



def parse_message(message) -> tuple:
    try:
        data = json.loads(message)
        return (
            data["engine_id"],  # Key by engine_id
            data["timestamp"],
            float(data["temp_air"]),
            float(data["temp_oil"]),
            float(data["temp_exhaust"]),
            float(data["vibration"]),
            float(data["pressure_1"]),
            float(data["pressure_2"]),
            int(data["rpm"])
        )
    except Exception as e:
        print(f"❌ Error parsing message: {message}, {e}")
        return None

def state_access_demo():
    env = StreamExecutionEnvironment.get_execution_environment()

    # kafka_source = KafkaSource.builder() \
    #     .set_bootstrap_servers(KAFKA_BROKER) \
    #     .set_topics(KAFKA_TOPIC) \
    #     .set_group_id("my-group") \
    #     .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
    #     .set_value_only_deserializer(SimpleStringSchema()) \
    #     .build()

    # watermark_strategy = WatermarkStrategy \
    #     .for_bounded_out_of_orderness(Duration.of_seconds(5)) \
    #     .with_timestamp_assigner(MyTimestampAssigner())


    # ds = env.from_source(
    #     source=kafka_source,
    #     watermark_strategy=watermark_strategy,
    #     source_name="kafka_source"
    # )

    consumer = FlinkKafkaConsumer(
        topics=KAFKA_TOPIC,
        deserialization_schema=SimpleStringSchema(),
        properties={"bootstrap.servers": KAFKA_BROKER, "group.id": "flink-group"}
    )

    consumer.set_start_from_earliest()

    ds = env.add_source(consumer)


    ds = ds.map(parse_message).filter(lambda x: x is not None)

    ds = ds.assign_timestamps_and_watermarks(
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
                         .with_timestamp_assigner(MyTimestampAssigner()))

    ds.key_by(lambda value: value[0]) \
        .process(Sum()) \
        .print()



    # apply the process function onto a keyed stream
    # ds.key_by(lambda value: value[0]) \
    #   .window(TumblingEventTimeWindows.of(Time.seconds(5))) \
    #   .process(Sum())

    # show(ds, env)

    # submit for execution
    env.execute()


if __name__ == '__main__':
    state_access_demo()
