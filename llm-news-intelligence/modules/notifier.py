# ============================================================
#  modules/notifier.py  –  Pushover bildirim gönderici
# ============================================================

import logging
import requests
from config.settings import PUSHOVER_TOKEN, PUSHOVER_USER, PUSHOVER_PRIORITY
from datetime import datetime
import os
logger = logging.getLogger(__name__)

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"




def send_notification(title: str, message: str, priority: int = PUSHOVER_PRIORITY) -> bool:
    """Pushover üzerinden bildirim gönderir."""
    payload = {
        "token":    PUSHOVER_TOKEN,
        "user":     PUSHOVER_USER,
        "title":    title,
        "message":  message,
        "priority": priority,
    }

    try:
        resp = requests.post(PUSHOVER_URL, data=payload, timeout=10)
        resp.raise_for_status()
        logger.info(f"Bildirim gönderildi: {title}")
        return True
    except Exception as e:
        logger.error(f"Pushover hatası: {e}")
        return False


def format_stock_notification(result: dict) -> tuple[str, str]:
    """Analiz sonucunu Pushover için title + message formatına çevirir."""
    ticker  = result["ticker"]
    price   = result["price"]
    change  = result["change"]
    analysis = result["analysis"]

    # Değişime göre emoji
    if change > 2:
        trend = "🚀"
    elif change > 0:
        trend = "📈"
    elif change < -2:
        trend = "🔴"
    else:
        trend = "📉"

    title = f"{trend} {ticker}  ${price}  ({change:+.2f}%)"

    # Pushover mesaj limiti ~1024 karakter
    message = analysis[:900] + ("..." if len(analysis) > 900 else "")

    return title, message


def send_stock_alerts(results: list[dict]) -> None:
    """Birden fazla hisse analizini bildirim olarak gönderir."""
    if not results:
        logger.warning("Gönderilecek analiz sonucu yok.")
        return

    for result in results:
        title, message = format_stock_notification(result)
        success = send_notification(title, message)
        if not success:
            logger.error(f"{result['ticker']} bildirimi gönderilemedi.")


def send_summary_notification(results: list[dict]) -> None:
    """
    Tüm hisseler için tek bir özet bildirim gönderir.
    Çok hisse varsa bu yöntem daha temiz olabilir.
    """
    if not results:
        return

    lines = []
    for r in results:
        change = r["change"]
        trend  = "▲" if change > 0 else "▼"
        # Sadece ilk satırı al (SINYAL: ... kısmı)
        first_line = r["analysis"].split("\n")[0] if r["analysis"] else "N/A"
        lines.append(f"{trend} {r['ticker']} ${r['price']} ({change:+.2f}%)\n   {first_line}")

    title   = f"📊 Hisse Analizi – {len(results)} hisse"
    message = "\n\n".join(lines)

    send_notification(title, message[:1000])

def save_to_notebook(results: list[dict]) -> None:
        with open("logs/notebook.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{'─' * 40}\n")
            f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"{'─' * 40}\n")
            for r in results:
                change = r["change"]
                trend = "🚀" if change > 2 else "📈" if change > 0 else "🔴" if change < -2 else "📉"
                f.write(f"{trend} {r['ticker']}  ${r['price']}  ({change:+.2f}%)\n")
