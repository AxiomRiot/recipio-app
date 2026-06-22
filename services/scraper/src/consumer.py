from confluent_kafka import Consumer, KafkaError
from pydantic import ValidationError
from schemas import ScrapeRequestedEventSchema
from producer import ScraperProducer
from parser import RecipeParser
from logger import get_color_logger

logger = get_color_logger("ScraperService")

class ScraperConsumer:
  running = False
  polling_timeout_sec = 1.0

  def __init__(self, config, polling_timeout_sec, parser, producer):
    self.consumer = Consumer(config)
    self.polling_timeout_sec = polling_timeout_sec
    self.parser = parser
    self.producer = producer

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

      data = raw.value.decode('utf-8')
      logger.debug(f"Received message: Key={raw.key().decode('utf-8')} Value={data}")

      try:
        scrape_request = ScrapeRequestedEventSchema(**data)

        logger.info(f"Received scrape request for url: {scrape_request.url}")
        recipe = self.parser.scrape_url(scrape_request.url)

        self.producer.send_event("recipe-parsed", recipe)

      except ValidationError as e:
        logger.error(e.errors())

  def stop(self):
    self.running = False
    self.consumer.close()