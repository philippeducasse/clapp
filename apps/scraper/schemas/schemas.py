from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ScrapedFestival(BaseModel):
    name: str
    website_url: Optional[str] = None
    country: Optional[str] = None
    town: Optional[str] = None

