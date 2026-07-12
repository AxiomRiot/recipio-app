from py_utils.schema.RecipeParsedEvent import RecipeParsedEvent, Header, Payload, Ingredient
from datetime import datetime
from fractions import Fraction
import re
import requests
from bs4 import BeautifulSoup
import uuid
import json
from logger import get_json_logger
from recipe_scrapers import scrape_html, WebsiteNotImplementedError

logger = get_json_logger("ScraperService")

class RecipeParser:
  UNIT_ALIASES: dict[str, str] = {
    "cup": "cup", "cups": "cup",
    "tablespoon": "tablespoon", "tablespoons": "tablespoon", "tbsp": "tablespoon", "tbsps": "tablespoon",
    "teaspoon": "teaspoon", "teaspoons": "teaspoon", "tsp": "teaspoon", "tsps": "teaspoon",
    "ounce": "ounce", "ounces": "ounce", "oz": "ounce",
    "pound": "pound", "pounds": "pound", "lb": "pound", "lbs": "pound",
    "gram": "gram", "grams": "gram", "g": "gram",
    "kilogram": "kilogram", "kilograms": "kilogram", "kg": "kilogram",
    "milliliter": "milliliter", "milliliters": "milliliter", "ml": "milliliter",
    "liter": "liter", "liters": "liter", "l": "liter",
    "pinch": "pinch", "pinches": "pinch",
    "clove": "clove", "cloves": "clove",
    "can": "can", "cans": "can",
    "slice": "slice", "slices": "slice",
    "stick": "stick", "sticks": "stick",
  }

  VULGAR_FRACTIONS: dict[str, str] = {
    "¼": "1/4", "½": "1/2", "¾": "3/4",
    "⅓": "1/3", "⅔": "2/3",
    "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
    "⅙": "1/6", "⅚": "5/6",
    "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
  }

  _NUMBER = r"\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+"
  _QUANTITY_RE = re.compile(rf"^({_NUMBER})(?:\s*-\s*({_NUMBER}))?\s*")
  _UNIT_RE = re.compile(r"([A-Za-z]+)(\s+|$)")

  def __init__(self):
    pass

  @staticmethod
  def _parse_number(token: str) -> float:
    token = token.strip()
    if " " in token:
      whole, frac = token.split(" ", 1)
      return float(whole) + float(Fraction(frac))
    if "/" in token:
      return float(Fraction(token))
    return float(token)

  @staticmethod
  def _resolve_scraper_value(scraper, attr_name: str):
    value = getattr(scraper, attr_name)
    if callable(value):
      return value()
    return value

  def extract_json_ld(self, html: str) -> dict | None:
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup.find_all('script', type='application/ld+json'):
      try:
        data = json.loads(tag.string)
        if isinstance(data, dict) and '@graph' in data:
            data = next((d for d in data['@graph'] if isinstance(d, dict) and d.get('@type') == 'Recipe'), None)
        elif isinstance(data, list):
            data = next((d for d in data if isinstance(d, dict) and d.get('@type') == 'Recipe'), None)
        if isinstance(data, dict) and data.get('@type') == 'Recipe':
            return data
      except json.JSONDecodeError:
        continue
    return None
    
  def get_html(self, url: str) -> str | None:
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
      return response.text
    else:
      logger.error(f"Failed to retrieve {url} with status code: {response.status_code}")
  
  def parse_ingredient_list(self, raw_ingredients: list[str]) -> list[Ingredient]:
    ingredients = []
    for raw_ingredient in raw_ingredients:
      text = raw_ingredient.strip()
      for char, replacement in self.VULGAR_FRACTIONS.items():
        text = text.replace(char, replacement)

      match = self._QUANTITY_RE.match(text)
      if match:
        low = self._parse_number(match.group(1))
        high = self._parse_number(match.group(2)) if match.group(2) else None
        quantity = (low + high) / 2 if high is not None else low
        remainder = text[match.end():]
      else:
        quantity = 0.0
        remainder = text

      unit = None
      word_match = self._UNIT_RE.match(remainder)
      if word_match:
        canonical = self.UNIT_ALIASES.get(word_match.group(1).lower())
        if canonical:
          unit = canonical
          remainder = remainder[word_match.end():]

      ingredients.append(Ingredient(name=remainder.strip(), quantity=quantity, unit=unit))
    return ingredients

  def scrape_url(self, url: str) -> dict | None:
    recipe_html = self.get_html(url)
    try:
      scraper = scrape_html(recipe_html, org_url=url)
    except WebsiteNotImplementedError:
      logger.error(f"{url} currently not supported by recipe-parser lib!")
      #TODO: try JSON-LD
      pass

    resolve = lambda attr: self._resolve_scraper_value(scraper, attr)

    return RecipeParsedEvent(
      header=Header(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime("%Y-%m-%d")
      ),
      event_type="recipe-parsed",
      payload=Payload(
        title=resolve("title"),
        url=url,
        site_name=resolve("site_name"),
        description=resolve("description"),
        category=resolve("category"),
        cuisine=resolve("cuisine"),
        image_url=resolve("image"),
        servings=resolve("yields"),
        nutrients=resolve("nutrients"),
        prep_time_min=resolve("prep_time"),
        cook_time_min=resolve("cook_time"),
        ratings=resolve("ratings"),
        ratings_count=resolve("ratings_count"),
        ingredients=self.parse_ingredient_list(resolve("ingredients")),
        steps=resolve("instructions_list")
      )
    )
