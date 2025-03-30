from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NewsArticle(BaseModel):
    title: str
    source: str
    description: Optional[str]
    url: str
    date: str
    image: Optional[str]

class WikipediaSummary(BaseModel):
    summary: str
    url: str

class ResearchContext(BaseModel):
    query: str
    news: List[NewsArticle]
    wiki: WikipediaSummary
    ai_response: str
    last_updated: datetime