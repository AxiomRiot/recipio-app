from py_utils.schema.RecipeParsedEvent import RecipeParsedEvent
from py_utils.schema.ScrapeRequestedEvent import ScrapeRequestedEvent
from py_utils.topics import TOPICS

EVENT_TOPICS_BY_SCHEMA = {
  TOPICS["RECIPE_PARSED"]: RecipeParsedEvent,
  TOPICS["SCRAPE_REQUESTED"]: ScrapeRequestedEvent
}

