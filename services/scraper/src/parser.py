from py_utils.schema.RecipeParsedEvent import RecipeParsedEvent, Header, Payload
from datetime import datetime
import uuid

class RecipeParser:
  def __init__(self):
    pass
  
  def scrape_url(self, url):
    return RecipeParsedEvent(
      header=Header(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime("%Y-%m-%d")
      ),
      event_type="recipe-parsed",
      payload=Payload(
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