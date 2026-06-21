import json
from confluent_kafka import Producer

# Configuration for connecting to the local Kafka broker
config = {
  'bootstrap.servers': 'localhost:9092', # Change if using a remote cluster
  'client.id': 'python-producer'
}

producer = Producer(config)

def delivery_report(err, msg):
    """ Triggered once for each message to check if delivery succeeded or failed. """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Sample streaming data
topic_name = 'user-activity'
data = {'user_id': 123, 'action': 'click', 'page': 'homepage'}

# Produce the message asynchronously
producer.produce(
    topic=topic_name,
    key=str(data['user_id']),
    value=json.dumps(data).encode('utf-8'),
    callback=delivery_report
)

# Wait for any outstanding messages to be delivered
producer.flush()
