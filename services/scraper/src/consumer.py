import json

from confluent_kafka import Consumer, KafkaError
from pydantic import ValidationError
from producer import ScraperProducer
from parser import RecipeParser
from logger import get_json_logger

from py_utils.events import EVENT_TOPICS_BY_SCHEMA

logger = get_json_logger("ScraperService")

class ScraperConsumer:
  running = False
  polling_timeout_sec = 1.0
  handle_func_map = {}

  def __init__(self, config, polling_timeout_sec):
    self.consumer = Consumer(config)
    self.polling_timeout_sec = polling_timeout_sec

  def register_handle_func(self, topic, handle_func):
    if topic not in self.handle_func_map:
      logger.info(f"Registering handle function for topic: {topic}")
      self.handle_func_map[topic] = handle_func
    else:
      logger.error(f"Handle function already exists for topic: {topic}")

  def subscribe(self, topic):
    self.consumer.subscribe([topic])

    self.running = True
    while self.running:
      raw = self.consumer.poll(timeout=self.polling_timeout_sec)

      if raw is None:
        continue
      if raw.error():
        if raw.error().code() == KafkaError._PARTITION_EOF:
          # Reached end of the partition
          continue
        else:
          logger.error(f"Consumer error: {raw.error()}")
          continue

      data = raw.value().decode('utf-8')
      logger.debug(f"Received message: Key={raw.key().decode('utf-8')} Value={data}")
      payload = json.loads(data)
      try:
        validated_data = EVENT_TOPICS_BY_SCHEMA[topic].model_validate(payload)
      except ValidationError:
        logger.error()
      else:
        self.handle_func_map[topic](validated_data)
        
  def stop(self):
    self.running = False
    self.consumer.close()