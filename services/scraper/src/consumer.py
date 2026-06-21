from confluent_kafka import Consumer, KafkaError
from schemas import ScrapeRequestEvent
import json

config = {
  'bootstrap.servers': 'localhost:9092',
  'group.id': 'python-consumer-group',  # Defines the consumer group instance
  'auto.offset.reset': 'earliest'        # Start reading from the beginning if no offset exists
}

consumer = Consumer(config)
consumer.subscribe('scrape-requested')

try:
  while True:
    # Poll for new messages (timeout in seconds)
    msg = consumer.poll(timeout=1.0)

    if msg is None:
      continue
    if msg.error():
      if msg.error().code() == KafkaError._PARTITION_EOF:
        # Reached the end of the partition
        continue
      else:
          print(f"Consumer error: {msg.error()}")
          break

    # Process the valid message
    print(f"Received message: Key={msg.key().decode('utf-8')} Value={msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass
finally:
    # Close down consumer cleanly to commit final offsets
    consumer.close()