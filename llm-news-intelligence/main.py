#!/usr/bin/env python3
# ============================================================
#  main.py  –  v4 (AI Manager fallback version)
# ============================================================

import logging
import sys
import time

from datetime import datetime, timezone

from config.settings import (
    WATCHLIST, RUN_ONLY_MARKET_HOURS,
    MARKET_OPEN_HOUR_UTC, MARKET_CLOSE_HOUR_UTC
)

from modules.stock_data import analyze_ticker
from modules.news_fetcher import fetch_news_for_ticker
from modules.screener import run_screener
from modules.opportunity_analyzer import send_daily_opportunity_report
from modules.notifier import send_stock_alerts, send_notification, save_to_notebook

from modules.ai_manager import AIManager
from modules.prompt_builder import build_prompt


# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/analyzer.log", encoding="utf-8"),
    ]
)

logger = logging.getLogger("main")

ai = AIManager()   # ✅ KRİTİK FIX: AI manager instance


DAILY_REPORT_HOUR_UTC = 17  # 12:00 ET = 17:00 UTC


# ============================================================
# MARKET CHECK
# ============================================================
def is_market_hours() -> bool:
    now = datetime.now(timezone.utc)

    if now.weekday() > 4:
        logger.info("Hafta sonu – atlanıyor.")
        return False

    if not (MARKET_OPEN_HOUR_UTC <= now.hour <= MARKET_CLOSE_HOUR_UTC):
        logger.info(f"Piyasa saati dışı (UTC {now.hour}:00) – atlanıyor.")
        return False

    return True


def is_daily_report_time() -> bool:
    now = datetime.now(timezone.utc)
    return now.hour == DAILY_REPORT_HOUR_UTC


# ============================================================
# WATCHLIST ANALYSIS
# ============================================================
def run_watchlist_analysis():
    logger.info("── WATCHLIST ANALİZİ ──")

    results = []

    for ticker in WATCHLIST:

        stock_data = analyze_ticker(ticker)
        if not stock_data:
            continue

        news = fetch_news_for_ticker(ticker)

        # prompt build (Gemini formatı ama artık model bağımsız)
        prompt = build_prompt(stock_data, news)

        try:
            analysis = ai.analyze_news(prompt)   # ✅ FALLBACK SYSTEM

            result = {
                "ticker": stock_data["ticker"],
                "analysis": analysis,
                "price": stock_data["price_data"]["price"],
                "change": stock_data["price_data"]["change_pct"],
            }

            results.append(result)

        except Exception as e:
            logger.error(f"{ticker} AI analiz hatası: {e}")

    if results:
        send_stock_alerts(results)
        save_to_notebook(results)
    else:
        send_notification("⚠️ Watchlist", "Hiç analiz üretilemedi.")


# ============================================================
# DAILY RADAR
# ============================================================
def run_daily_radar():
    logger.info("── GÜNLÜK FIRSAT RAPORU ──")

    candidates = run_screener()
    send_daily_opportunity_report(candidates)


# ============================================================
# MAIN LOOP
# ============================================================
def run_analysis():

    logger.info("=" * 55)
    logger.info(f"  Çalışma: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 55)

    if RUN_ONLY_MARKET_HOURS and not is_market_hours():
        return

    run_watchlist_analysis()

    if is_daily_report_time():
        run_daily_radar()

    logger.info("Tamamlandı.")


if __name__ == "__main__":

    while True:
        run_analysis()

        now = datetime.now()

        seconds_to_next_hour = (60 - now.minute) * 60 - now.second

        logger.info(
            f"Sonraki çalışma: {seconds_to_next_hour // 60} dakika sonra (saat başı)"
        )

        time.sleep(seconds_to_next_hour)