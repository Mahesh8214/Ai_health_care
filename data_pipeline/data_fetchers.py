import requests
import wikipedia
from datetime import datetime, timedelta
from config import settings
from .data_models import NewsArticle, WikipediaSummary

def fetch_news(query: str, days_old: int = 1) -> list[NewsArticle]:
    try:
        date_from = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={settings.NEWS_API_KEY}&pageSize=5&sortBy=publishedAt&from={date_from}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        return [
            NewsArticle(
                title=a["title"],
                source=a["source"]["name"],
                description=a.get("description"),
                url=a["url"],
                date=datetime.strptime(a["publishedAt"][:10], "%Y-%m-%d").strftime("%b %d, %Y"),
                image=a.get("urlToImage")
            ) for a in articles if a.get("title")
        ]
    except Exception as e:
        raise Exception(f"News API error: {str(e)}")

def get_wikipedia_summary(query: str) -> WikipediaSummary:
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return WikipediaSummary(summary="", url="")
        
        page = wikipedia.page(search_results[0], auto_suggest=True)
        return WikipediaSummary(
            summary=page.summary[:500],
            url=page.url
        )
    except Exception as e:
        raise Exception(f"Wikipedia error: {str(e)}")