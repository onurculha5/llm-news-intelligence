# ============================================================
#  modules/finnhub_news.py  –  Finnhub haber + sentiment
# ============================================================

import logging
import requests
from datetime import datetime, timedelta, timezone
from config.settings import FINNHUB_API_KEY

logger = logging.getLogger(__name__)

FINNHUB_NEWS_URL      = "https://finnhub.io/api/v1/company-news"
FINNHUB_SENTIMENT_URL = "https://finnhub.io/api/v1/news-sentiment"


def fetch_finnhub_news(ticker: str, days_back: int = 3) -> list[dict]:
    """Ticker bazlı son haberleri çeker."""
    to_date   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "symbol": ticker,
        "from":   from_date,
        "to":     to_date,
        "token":  FINNHUB_API_KEY,
    }

    try:
        resp = requests.get(FINNHUB_NEWS_URL, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json()

        results = []
        for art in articles[:5]:   # En fazla 5 haber
            results.append({
                "title":     art.get("headline", ""),
                "summary":   art.get("summary", ""),
                "source":    art.get("source", ""),
                "published": datetime.fromtimestamp(art.get("datetime", 0)).strftime("%Y-%m-%d %H:%M"),
                "url":       art.get("url", ""),
            })

        logger.info(f"{ticker}: Finnhub'dan {len(results)} haber alındı.")
        return results

    except Exception as e:
        logger.error(f"{ticker} Finnhub haber hatası: {e}")
        return []


def fetch_sentiment(ticker: str) -> dict | None:
    """
    Finnhub'ın hazır sentiment skorunu çeker.
    buzz.buzz       → haber hacmi (normalden yüksek mi?)
    sentiment.bearishPercent / bullishPercent → piyasa duyarlılığı
    """
    params = {
        "symbol": ticker,
        "token":  FINNHUB_API_KEY,
    }

    try:
        resp = requests.get(FINNHUB_SENTIMENT_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        buzz      = data.get("buzz", {})
        sentiment = data.get("sentiment", {})

        result = {
            "buzz_score":      round(buzz.get("buzz", 0), 3),
            "articles_weekly": buzz.get("weeklyAverage", 0),
            "bullish_pct":     round(sentiment.get("bullishPercent", 0) * 100, 1),
            "bearish_pct":     round(sentiment.get("bearishPercent", 0) * 100, 1),
        }

        # Genel sentiment etiketi
        if result["bullish_pct"] > 60:
            result["label"] = "Yükseliş"
        elif result["bearish_pct"] > 60:
            result["label"] = "Düşüş"
        else:
            result["label"] = "Nötr"

        logger.info(f"{ticker}: Sentiment → {result['label']} "
                    f"(🐂 %{result['bullish_pct']} / 🐻 %{result['bearish_pct']})")
        return result

    except Exception as e:
        logger.error(f"{ticker} Finnhub sentiment hatası: {e}")
        return None


def fetch_full_finnhub_data(ticker: str) -> dict:
    """Haber + sentiment'i birlikte döner."""
    return {
        "ticker":    ticker,
        "news":      fetch_finnhub_news(ticker),
        "sentiment": fetch_sentiment(ticker),
    }
