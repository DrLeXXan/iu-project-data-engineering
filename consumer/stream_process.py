import datetime
import json
from typing import Iterable

from pyflink.common import WatermarkStrategy, Duration, Time
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext, AggregateFunction, ProcessWindowFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream.window import TumblingEventTimeWindows



# Kafka consumer settings
KAFKA_BROKER = "kafka:9093"
KAFKA_TOPIC = "factory_001"


class AverageAggregate(AggregateFunction):

    def create_accumulator(self) -> tuple[int, int]:
        return 0, 0

    def add(self, value: tuple[str, int], accumulator: tuple[int, int]) -> tuple[int, int]:
        # print(value)
        # print(f"accumulator: {accumulator[0]}, accumulator2: {accumulator[1]}")
        return accumulator[0] + value[2], accumulator[1] + 1

    def get_result(self, accumulator: tuple[int, int]) -> float:
        print(f"Get_Result: {accumulator[0] / accumulator[1]}")
        return accumulator[0] / accumulator[1]

    def merge(self, a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        return a[0] + b[0], a[1] + b[1]

class MyProcessWindowFunction(ProcessWindowFunction):

    def process(self, key: str, context: ProcessWindowFunction.Context,
                averages: Iterable[float]) ->Iterable[tuple[str, float]]:
        average = next(iter(averages))
        print(f"Key: {key}, Average: {average}")
        yield key, average

class Sum(KeyedProcessFunction):

    def __init__(self):
        self.state = None

    def open(self, runtime_context: RuntimeContext):
        self.state = runtime_context.get_state(ValueStateDescriptor(
            "my_state", Types.PICKLED_BYTE_ARRAY()))

    def process_element(self, value, ctx: 'KeyedProcessFunction.Context'):
        # retrieve the current count
        current = self.state.value()

        if current is None:
            current = [0,0]

        # update the state's count
        current[0] += value[2]

        # set the state's timestamp to the record's assigned event time timestamp
        current[1] = ctx.timestamp()

        # write the state back
        self.state.update(current)

        print(f"📌 Watermark: {ctx.timer_service().current_watermark()}, Data: {value}")

        # schedule the next timer 60 seconds from the current event time
        ctx.timer_service().register_event_time_timer(current[1] + 5000)

    def on_timer(self, timestamp: int, ctx: 'KeyedProcessFunction.OnTimerContext'):
        # get the state for the key that scheduled the timer
        result = self.state.value()

        # check if this is an outdated timer or the latest timer
        if timestamp == result[1] + 5000:
            # emit the state on timeout
            print("------------------------------On_TIMER FUNCTION -------------------------------")
            yield result[0], result[1]

class MyTimestampAssigner(TimestampAssigner):

    def __init__(self):
        self.epoch = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)

    def extract_timestamp(self, value, record_timestamp) -> int:
        event_time = datetime.datetime.strptime(value[1], "%Y-%m-%d %H:%M:%S")
        print(self.epoch)
        print(event_time)
        return int((event_time - self.epoch).total_seconds() * 1000)



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

if __name__ == '__main__':
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(KAFKA_BROKER) \
        .set_topics(KAFKA_TOPIC) \
        .set_group_id("my-group") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    watermark_strategy = WatermarkStrategy \
        .for_monotonous_timestamps() \
        .with_timestamp_assigner(MyTimestampAssigner())

    ds = env.from_source(
        source=kafka_source,
        watermark_strategy=watermark_strategy,
        source_name="kafka_source")


    ds = ds.map(parse_message).filter(lambda x: x is not None)

    result = ds.key_by(lambda value: value[0]) \
        .window(TumblingEventTimeWindows.of(Time.seconds(5))) \
        .aggregate(AverageAggregate(),
                   window_function=MyProcessWindowFunction(),
                accumulator_type=Types.TUPLE([Types.LONG(), Types.LONG()]),
                output_type=Types.TUPLE([Types.STRING(), Types.DOUBLE()])) \
        .print()

    env.execute()
