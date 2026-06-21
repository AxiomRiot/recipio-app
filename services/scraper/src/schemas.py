from typing import Optional
from pydantic import BaseModel
import datetime

class ScrapeRequestPayload(BaseModel):
  url: str
  user_id: str

class ScrapeRequestEvent(BaseModel):
  event_id: str
  event_type: str = "scrape-requested"
  timestamp: datetime
  payload: ScrapeRequestPayload

class Ingredient(BaseModel):
  name: str
  quantity: float
  unit: Optional[str] = None

class Duration(BaseModel):
  days: str
  hours: str
  minutes: str

class RecipeParsedPayload(BaseModel):
  title: str
  url: str
  description: str
  servings: str
  duration: Duration
  ingredients: list[Ingredient]
  steps: list[str]
  image: list[float]

class RecipeParsedEvent(BaseModel):
  event_id: str
  event_type: str = "recipe-parsed"
  timestamp: datetime
  payload: RecipeParsedPayload
