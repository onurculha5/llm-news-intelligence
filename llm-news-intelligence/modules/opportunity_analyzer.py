# ============================================================
#  modules/opportunity_analyzer.py  –  v3
#  Tüm adaylar → Finnhub → Gemini → Pushover
# ============================================================

import logging
import requests
from config.settings import GEMINI_API_KEY
from modules.notifier import send_notification, PUSHOVER_PRIORITY
from modules.finnhub_news import fetch_full_finnhub_data
from modules.mail_sender import send_opportunity_mail

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def build_opportunity_prompt(candidates: list[dict]) -> str:
    sections = []

    for c in candidates:
        ticker    = c["ticker"]
        sector    = c["sector"]
        price     = c["data"]["price_data"]
        indics    = c["data"]["indicators"]
        signals   = c["signals"]
        finnhub   = c.get("finnhub", {})
        news      = finnhub.get("news", [])
        sentiment = finnhub.get("sentiment") or {}

        news_lines = ""
        for i, art in enumerate(news[:3], 1):
            news_lines += f"  {i}. [{art['source']}] {art['title']}\n"
        if not news_lines:
            news_lines = "  Haber bulunamadı.\n"

        sent_str = "N/A"
        if sentiment:
            sent_str = (
                f"{sentiment.get('label','N/A')} "
                f"(🐂%{sentiment.get('bullish_pct',0)} "
                f"🐻%{sentiment.get('bearish_pct',0)})"
            )

        section = f"""
━━━ {ticker} ({sector}) ━━━
Fiyat : ${price['price']} ({price['change_pct']:+.2f}%)
RSI   : {indics.get('RSI','N/A')} | MACD Hist: {indics.get('MACD_Hist','N/A')}
SMA   : {indics.get('SMA_20','N/A')} / {indics.get('SMA_50','N/A')} / {indics.get('SMA_200','N/A')}
Sentiment: {sent_str}
Sinyaller: {', '.join(signals)}
Haberler:
{news_lines}""".strip()
        sections.append(section)

    all_sections = "\n\n".join(sections)

    prompt = f"""
Sen deneyimli bir hisse senedi analistsin. Aşağıdaki hisseler bugün teknik screener'dan geçti. Her birini kısaca değerlendir.

{all_sections}

Her hisse için TAM OLARAK şu formatta yaz (başka bir şey ekleme):

[TICKER] | [AL / İZLE / RİSKLİ] | [1 cümle teknik+haber özeti] | 🎯[kısa vadeli seviye]

Sonuna şunu ekle:
🏆 GÜNÜN EN İYİSİ: [ticker] — [1 cümle neden]

Türkçe yaz. Her satır max 120 karakter. Toplam 250 kelimeyi geçme.
""".strip()

    return prompt


def analyze_all_candidates(candidates: list[dict]) -> str | None:
    if not candidates:
        return None

    prompt = build_opportunity_prompt(candidates)
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

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=45
        )
        resp.raise_for_status()
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )
        return text.strip()

    except Exception as e:
        logger.error(f"Gemini fırsat analizi hatası: {e}")
        return None


def send_daily_opportunity_report(candidates: list[dict]) -> None:
    """Saat 12:00'de çağrılır — tüm adayların günlük raporu."""
    if not candidates:
        send_notification(
            "📊 Günlük Fırsat Raporu",
            "Bugün screener'dan geçen hisse bulunamadı."
        )
        return

    logger.info(f"Günlük rapor: {len(candidates)} aday için Finnhub verisi çekiliyor...")

    # Tüm adaylar için Finnhub çek
    for c in candidates:
        c["finnhub"] = fetch_full_finnhub_data(c["ticker"])

    # Gemini analizi
    logger.info("Gemini günlük analiz yapıyor...")
    analysis = analyze_all_candidates(candidates)

    if not analysis:
        logger.warning("Günlük analiz alınamadı.")
        return

    ticker_list = " · ".join(c["ticker"] for c in candidates)
    title   = f"📊 Günlük Fırsat Raporu — {len(candidates)} hisse"
    header  = f"🔍 Radar: {ticker_list}\n\n"
    message = (header + analysis)[:1000]

    #send_notification(title, message, priority=PUSHOVER_PRIORITY)
    send_notification("📊 Fırsat Raporu Maile Gönderildi", f"🔍 {ticker_list}", priority=PUSHOVER_PRIORITY)
    send_opportunity_mail(candidates, analysis)
    logger.info("Günlük fırsat raporu gönderildi.")


def send_opportunity_alert(candidates: list[dict]) -> None:
    """3 saatlik döngüde çağrılır — kısa özet liste."""
    if not candidates:
        logger.info("Bu döngüde fırsat adayı yok.")
        return

    ticker_list = " · ".join(c["ticker"] for c in candidates)
    signal_lines = "\n".join(
        f"• {c['ticker']} ({c['sector'][0:4]}) — {len(c['signals'])} sinyal"
        for c in candidates
    )

    title   = f"🔍 Fırsat Radarı — {len(candidates)} aday"
    message = f"{ticker_list}\n\n{signal_lines}\n\n📊 Detaylı analiz saat 12:00'de gelecek."

    send_notification(title, message, priority=PUSHOVER_PRIORITY)
    logger.info(f"Radar özeti gönderildi: {ticker_list}")
