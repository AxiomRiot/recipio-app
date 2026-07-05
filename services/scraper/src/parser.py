from schemas import EventHeaderSchema
from schemas import RecipeParsedEventSchema, RecipeParsedPayload, EventHeaderSchema
from datetime import datetime
import uuid

class RecipeParser:
  def __init__(self):
    pass
  
  def scrape_url(self, url):
    event_header = EventHeaderSchema(
      event_id=str(uuid.uuid4()),
      timestamp=datetime.now().strftime("%Y-%m-%d")
    )

    return RecipeParsedEventSchema(
      header=event_header,
      event_type="recipe-parsed",
      payload=RecipeParsedPayload(
        title="test",
        url=url,
        description="",
        servings="test",
        duration={
          "days": 3,
          "hours": 4,
          "minutes": 5
        },
        ingredients=[],
        steps=[]
      )
    )