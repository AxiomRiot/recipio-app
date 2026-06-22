import json
from confluent_kafka import Producer
from logger import get_color_logger

logger = get_color_logger("ScraperService")

class ScraperProducer:
    def __init__(self, config):
        self.producer = Producer(config)

    def delivery_report(self, err, msg):
      """ Triggered once for each message to check if delivery succeeded or failed. """
      if err is not None:
          logger.error(f"Message delivery failed: {err}")
      else:
          logger.error(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    def send_event(self, topic, event):
      event_json = event.model_dump_json()
      logger.info(f"Sending event with key {event.event_id}: {event_json}")

      self.producer.produce(
        topic=topic,
        key=str(event.event_id),
        value=event_json.encode('utf-8'),
        callback=self.delivery_report 
      )
      self.producer.flush()   
