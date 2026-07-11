from producer import ScraperProducer
from parser import RecipeParser
from consumer import ScraperConsumer
from logger import get_json_logger

from py_utils.topics import TOPICS
from py_utils.schema import ScrapeRequestedEvent

logger = get_json_logger("ScraperService")

class ScraperCoordinator:
  def __init__(self, consumer, parser, producer):
    self.consumer: ScraperConsumer = consumer
    self.parser: RecipeParser = parser
    self.producer: ScraperProducer = producer

    self.consumer.register_handle_func(TOPICS["SCRAPE_REQUESTED"], self.handleScrapeRequestEvent)
  
  def handleScrapeRequestEvent(self, scrape_request: ScrapeRequestedEvent):
    logger.info(f"Received scrape request for url: {scrape_request.url}")
    recipe = self.parser.scrape_url(scrape_request.url)

    self.producer.send_event(TOPICS["RECIPE_PARSED"], recipe);

  def start(self):
    logger.info("Starting up ScraperService")
    self.consumer.subscribe(TOPICS["SCRAPE_REQUESTED"])

  def stop(self):
    logger.info("Stopping ScraperService")
    self.consumer.stop()