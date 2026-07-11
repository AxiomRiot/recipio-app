#!/usr/bin/env bash
set -euo pipefail

TOPICS_FILE="${TOPICS_FILE:-/topics.yml}"
BROKER="${KAFKA_BROKER:-kafka:9092}"
KAFKA_TOPICS_BIN="${KAFKA_TOPICS_BIN:-/opt/kafka/bin/kafka-topics.sh}"

echo "Reading topic config from $TOPICS_FILE..."

# yq parses the YAML and emits one line per topic as tab-separated fields
yq -r '.topics[] | [.name, .partitions, .replication_factor, .retention_ms, .cleanup_policy] | @tsv' "$TOPICS_FILE" |
while IFS=$'\t' read -r name partitions replication retention_ms cleanup_policy; do
  echo "Creating topic: $name (partitions=$partitions, retention=${retention_ms}ms)"

  "$KAFKA_TOPICS_BIN" \
    --bootstrap-server "$BROKER" \
    --create \
    --if-not-exists \
    --topic "$name" \
    --partitions "$partitions" \
    --replication-factor "$replication" \
    --config "retention.ms=$retention_ms" \
    --config "cleanup.policy=$cleanup_policy"
done

echo "All topics created."
