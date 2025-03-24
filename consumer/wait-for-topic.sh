#!/bin/bash

KAFKA_BROKER="kafka:9093"

echo "🔄 Waiting for Kafka at $KAFKA_BROKER to have at least one topic..."

# Wait until at least one topic exists
until kafka-topics.sh --bootstrap-server $KAFKA_BROKER --list | grep -q .; do
  echo "🚫 No topics found yet. Retrying in 5 seconds..."
  sleep 5
done

echo "✅ Found at least one Kafka topic. Starting Bytewax."

# Execute the main Bytewax application

KAFKA_BROKER="kafka:9093"

echo "🔄 Waiting for Kafka at $KAFKA_BROKER to have at least one topic..."

# Wait until at least one topic exists
until kafka-topics.sh --bootstrap-server $KAFKA_BROKER --list | grep -q .; do
  echo "🚫 No topics found yet. Retrying in 5 seconds..."
  sleep 5
done

echo "✅ Found at least one Kafka topic. Starting Bytewax."

# Execute the main Bytewax application
exec "$@"
