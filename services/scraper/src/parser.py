from schemas import EventHeaderSchema
from schemas import RecipeParsedEventSchema, RecipeParsedPayload
from datetime import datetime
import uuid

class RecipeParser:
  def __init__(self):
    pass
  
  def scrape_url(self, url):
    return RecipeParsedEventSchema(
      header=EventHeaderSchema(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime("%Y-%m-%d")
      ),
      event_type="recipe-parsed",
      payload=RecipeParsedPayload(
        title="test",
        url=url,
        description="",
        servings="test",
        duration={
          "hours": "3",
          "minutes": "4",
          "seconds": "5"
        },
        ingredients=[],
        steps=[]
      )
    )