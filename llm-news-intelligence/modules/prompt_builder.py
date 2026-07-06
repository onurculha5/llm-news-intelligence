# ============================================================
#  modules/gemini_analyzer.py  –  Google Gemini ile analiz
# ============================================================
import time
import logging
import requests
import json
from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def build_prompt(stock_analysis: dict, news: list[dict]) -> str:
    """Gemini için yapılandırılmış prompt oluşturur."""
    ticker = stock_analysis["ticker"]
    price  = stock_analysis["price_data"]
    indics = stock_analysis["indicators"]

    # Haber başlıkları
    news_lines = ""
    for i, article in enumerate(news[:5], 1):
        news_lines += f"  {i}. [{article['source']}] {article['title']}\n"
    if not news_lines:
        news_lines = "  Haber bulunamadı.\n"

    # İndikatör özeti
    rsi_val   = indics.get("RSI", "N/A")
    macd_val  = indics.get("MACD", "N/A")
    macd_sig  = indics.get("MACD_Signal", "N/A")
    macd_hist = indics.get("MACD_Hist", "N/A")
    bb_upper  = indics.get("BB_Upper", "N/A")
    bb_lower  = indics.get("BB_Lower", "N/A")
    sma_20    = indics.get("SMA_20", "N/A")
    sma_50    = indics.get("SMA_50", "N/A")
    sma_200   = indics.get("SMA_200", "N/A")
    stoch_k   = indics.get("Stoch_K", "N/A")
    atr       = indics.get("ATR_14", "N/A")

    prompt = f"""
Sen deneyimli bir hisse senedi analistsin. Aşağıdaki verileri değerlendirip kısa ve net bir analiz yap.

=== {ticker} ANALİZİ ===

📊 FİYAT BİLGİSİ:
  Güncel Fiyat : ${price['price']}
  Değişim      : %{price['change_pct']}
  Günlük Aralık: ${price['low']} – ${price['high']}
  Hacim        : {price['volume']:,}

📈 TEKNİK İNDİKATÖRLER:
  RSI (14)      : {rsi_val}  ← 30 altı aşırı satım, 70 üstü aşırı alım
  MACD          : {macd_val} | Sinyal: {macd_sig} | Histogram: {macd_hist}
  Stochastic %K : {stoch_k}
  Bollinger Üst : {bb_upper} | Alt: {bb_lower}
  SMA 20 / 50 / 200 : {sma_20} / {sma_50} / {sma_200}
  ATR (14)      : {atr}

📰 SON HABERLER:
{news_lines}

Lütfen şu formatta yanıt ver (emoji kullanabilirsin):

SINYAL: [GÜÇLÜ AL / AL / NÖTR / SAT / GÜÇLÜ SAT]
GÜVEN : [Düşük / Orta / Yüksek]
ÖZET  : (2-3 cümle, teknik + haber birlikte değerlendirmesi)
RİSKLER: (1-2 cümle)
İZLE  : (Dikkat edilmesi gereken seviye veya olay)

Yanıtını kısa tut, 100 kelimeyi geçme.Çünkü bildirimler pushover'a gidecek orada kelime fazla gelince kesiyor. Türkçe yaz.
""".strip()

    return prompt


def analyze_with_gemini(stock_analysis: dict, news: list[dict]) -> dict:
    prompt  = build_prompt(stock_analysis, news)
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    done    = False
    attempt = 0

    while not done:
        try:
            resp = requests.post(
                GEMINI_URL,
                params={"key": GEMINI_API_KEY},
                json=payload,
                timeout=30

            )
            if resp.status_code == 429:
                wait = 2 ** attempt * 5   # 5, 10, 20, 40 saniye
                logger.warning(f"429 − {wait}s bekleniyor (deneme {attempt+1})")
                time.sleep(wait)
                attempt += 1
                if attempt > 5:
                    raise Exception("Rate limit aşıldı, max deneme sayısına ulaşıldı.")
            else:
                resp.raise_for_status()
                done = True

        except Exception as e:
            logger.error(f"Gemini hatası ({stock_analysis['ticker']}): {e}")
            return {
                "ticker":   stock_analysis["ticker"],
                "analysis": f"Analiz alınamadı: {e}",
                "price":    stock_analysis["price_data"]["price"],
                "change":   stock_analysis["price_data"]["change_pct"],
            }

    data = resp.json()
    logger.info(f"Gemini response: {data}")

    text = (
    data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
)

    return {
        "ticker":   stock_analysis["ticker"],
        "analysis": text.strip(),
        "price":    stock_analysis["price_data"]["price"],
        "change":   stock_analysis["price_data"]["change_pct"],
    }