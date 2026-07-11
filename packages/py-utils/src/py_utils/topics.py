import json
from pathlib import Path

TOPICS = json.loads(
    (Path(__file__).parent.parent.parent.parent / "common" / "topics.json").read_text()
)
