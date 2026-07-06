# ============================================================
#  modules/news_fetcher.py  –  NewsAPI haber çekici
# ============================================================

import logging
import requests
from datetime import datetime, timedelta
from config.settings import NEWSAPI_KEY, NEWS_ARTICLE_COUNT

logger = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/everything"


def fetch_news(ticker: str, company_name: str = "") -> list[dict]:
    """
    Belirli bir hisse için son haberleri çeker.
    company_name verilirse daha iyi sonuç alınır (örn. "Apple" AAPL için).
    """
    query = f"{ticker} stock"
    if company_name:
        query = f"{company_name} OR {ticker} stock"

    from_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")

    params = {
        "q":          query,
        "from":       from_date,
        "sortBy":     "relevancy",
        "language":   "en",
        "pageSize":   NEWS_ARTICLE_COUNT,
        "apiKey":     NEWSAPI_KEY,
    }

    try:
        resp = requests.get(NEWSAPI_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        articles = data.get("articles", [])
        results = []
        for art in articles:
            results.append({
                "title":       art.get("title", ""),
                "description": art.get("description", ""),
                "source":      art.get("source", {}).get("name", ""),
                "published":   art.get("publishedAt", ""),
                "url":         art.get("url", ""),
            })

        logger.info(f"{ticker}: {len(results)} haber bulundu.")
        return results

    except Exception as e:
        logger.error(f"{ticker} haberleri çekilirken hata: {e}")
        return []


# Hisse → Şirket adı eşleştirmesi (NewsAPI için daha iyi arama)
TICKER_TO_COMPANY = {
    "ORCL":  "Oracle",
    "NVDA":  "NVIDIA",
    "MSFT":  "Microsoft",
    "SOUN": "SounHound AI",
    "MSTR":  "MicroStrategy",
    "VERI":  "Veritone"
}


def fetch_news_for_ticker(ticker: str) -> list[dict]:
    company = TICKER_TO_COMPANY.get(ticker, "")
    return fetch_news(ticker, company)
