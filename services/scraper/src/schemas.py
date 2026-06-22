from typing import Optional
from pydantic import BaseModel

class EventHeaderSchema(BaseModel):
  event_id: str
  timestamp: str

class ScrapeRequestedEventSchema(BaseModel):
  header: EventHeaderSchema
  event_type: str = "scrape-requested"
  url: str

class Ingredient(BaseModel):
  name: str
  quantity: float
  unit: Optional[str] = None

class RecipeParsedPayload(BaseModel):
  title: str
  url: str
  description: str
  servings: str
  duration: dict[str, str]
  ingredients: list[Ingredient]
  steps: list[str]

class RecipeParsedEventSchema(BaseModel):
  header: EventHeaderSchema
  event_type: str = "recipe-parsed"
  payload: RecipeParsedPayload
