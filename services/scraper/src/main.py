from producer import ScraperProducer
from consumer import ScraperConsumer
from parser import RecipeParser
from logger import get_color_logger

import tomllib
from pathlib import Path


def load_config(file_name="config.toml"):
  config_path = Path(file_name)
  with open(config_path, "rb") as f:
      return tomllib.load(f)

def main():
  logger = get_color_logger("ScraperService")
  logger.info("Starting up ScraperService")

  config = load_config()

  recipe_parser = RecipeParser()
  scraper_producer = ScraperProducer({
    'bootstrap.servers': config["producer"]["server"],
    'client.id': config["producer"]["client_id"]
  })
  scraper_consumer = ScraperConsumer(
    {
      'bootstrap.servers': config["consumer"]["server"],
      'group.id': config["consumer"]["group_id"],
      'auto.offset.reset': 'earliest' 
    },
    polling_timeout_sec=config["consumer"]["polling_interval_sec"],
    parser=recipe_parser,
    producer=scraper_producer 
  )
  
  scraper_consumer.subscribe("scrape-requested")

if __name__ == '__main__':
  main()