import json
from confluent_kafka import Producer
from logger import get_json_logger

logger = get_json_logger("ScraperService")

class ScraperProducer:
    def __init__(self, config):
        self.producer = Producer(config)

    def delivery_report(self, err, msg):
      """ Triggered once for each message to check if delivery succeeded or failed. """
      if err is not None:
          logger.error(f"Message delivery failed: {err}")
      else:
          logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    def send_event(self, topic, event):
      event_json = event.model_dump_json()
      event_id = event.header.event_id
      logger.info(f"Sending event with key {event_id}: {event_json}")

      self.producer.produce(
        topic=topic,
        key=str(event_id),
        value=event_json.encode('utf-8'),
        callback=self.delivery_report 
      )
      self.producer.flush()
