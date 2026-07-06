# ============================================================
#  modules/screener.py  –  Sektör evreni + teknik filtre
# ============================================================

import logging
from modules.stock_data import analyze_ticker

logger = logging.getLogger(__name__)

# ── Sektör bazlı ~30 hisselik evren ────────────────────────
SECTOR_UNIVERSE = {
    "Technology": [
        "AAPL", "MSFT", "NVDA", "AMD", "INTC",
        "AVGO", "QCOM", "CRM", "SNOW", "PLTR",
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG",
        "MPC", "PSX", "OXY",
    ],
    "Finance": [
        "JPM", "BAC", "GS", "MS", "WFC",
        "V", "MA", "BLK",
    ],
    "Healthcare": [
        "JNJ", "UNH", "LLY", "ABBV", "MRK",
    ],
}

# Düz liste (tüm sektörler birleşik)
ALL_UNIVERSE = [t for tickers in SECTOR_UNIVERSE.values() for t in tickers]


def get_sector(ticker: str) -> str:
    for sector, tickers in SECTOR_UNIVERSE.items():
        if ticker in tickers:
            return sector
    return "Other"


# ── Filtre kriterleri ───────────────────────────────────────

def _is_oversold_rsi(indics: dict) -> tuple[bool, str]:
    rsi = indics.get("RSI")
    if rsi and rsi < 38:
        return True, f"RSI aşırı satım bölgesinde ({rsi:.1f})"
    return False, ""


def _is_macd_crossover(indics: dict) -> tuple[bool, str]:
    """MACD histogram pozitife döndüyse (potansiyel yukarı kırılım)"""
    hist = indics.get("MACD_Hist")
    macd = indics.get("MACD")
    sig  = indics.get("MACD_Signal")
    if hist and macd and sig:
        if hist > 0 and macd > sig:
            return True, f"MACD sinyal üzerinde (hist: {hist:.4f})"
    return False, ""


def _is_near_sma200(indics: dict, price: float) -> tuple[bool, str]:
    """Fiyat SMA200'ün %3 içindeyse (destek seviyesi testi)"""
    sma200 = indics.get("SMA_200")
    if sma200 and price:
        diff_pct = abs((price - sma200) / sma200) * 100
        if diff_pct < 3.0:
            return True, f"SMA200 destek testinde (${sma200:.2f}, fark %{diff_pct:.1f})"
    return False, ""


def _is_sma_golden_cross(indics: dict) -> tuple[bool, str]:
    """SMA20 > SMA50 > SMA200 = güçlü trend"""
    s20  = indics.get("SMA_20")
    s50  = indics.get("SMA_50")
    s200 = indics.get("SMA_200")
    if s20 and s50 and s200 and s20 > s50 > s200:
        return True, f"Golden cross: SMA20({s20:.1f}) > SMA50({s50:.1f}) > SMA200({s200:.1f})"
    return False, ""


def _is_bollinger_squeeze(indics: dict) -> tuple[bool, str]:
    """BB genişliği daraldıysa büyük hareket yaklaşıyor olabilir"""
    bb_w = indics.get("BB_Width")
    if bb_w and bb_w < 0.05:
        return True, f"Bollinger sıkışması (genişlik: {bb_w:.4f})"
    return False, ""


def _is_stoch_oversold(indics: dict) -> tuple[bool, str]:
    k = indics.get("Stoch_K")
    d = indics.get("Stoch_D")
    if k and d and k < 25 and d < 25:
        return True, f"Stochastic aşırı satım (%K:{k:.1f}, %D:{d:.1f})"
    return False, ""


# ── Ana screener fonksiyonu ─────────────────────────────────

FILTERS = [
    _is_oversold_rsi,
    _is_macd_crossover,
    _is_bollinger_squeeze,
    _is_stoch_oversold,
    _is_sma_golden_cross
]

PRICE_FILTERS = [
    _is_near_sma200
]

MIN_SIGNALS = 2   # En az kaç filtreden geçmeli


def screen_ticker(ticker: str) -> dict | None:
    """
    Tek bir hisseyi tüm filtrelerden geçirir.
    Yeterli sinyal varsa dict döner, yoksa None.
    """
    # Watchlist'te zaten takip edilen hisseleri atla
    from config.settings import WATCHLIST
    if ticker in WATCHLIST:
        return None

    data = analyze_ticker(ticker)
    if data is None:
        return None

    indics = data["indicators"]
    price  = data["price_data"]["price"]
    signals = []

    # Fiyat gerektirmeyen filtreler
    for fn in FILTERS:
        passed, reason = fn(indics)
        if passed:
            signals.append(reason)

    # Fiyat gerektiren filtreler
    for fn in PRICE_FILTERS:
        passed, reason = fn(indics, price)
        if passed:
            signals.append(reason)

    if len(signals) < MIN_SIGNALS:
        return None

    return {
        "ticker":   ticker,
        "sector":   get_sector(ticker),
        "signals":  signals,
        "data":     data,
    }


def run_screener() -> list[dict]:
    """
    Tüm evreni tarar, filtreden geçen adayları döner.
    NewsAPI limitini korumak için haberleri burada çekmiyoruz.
    """
    logger.info(f"Screener başladı: {len(ALL_UNIVERSE)} hisse taranıyor...")
    candidates = []

    for ticker in ALL_UNIVERSE:
        logger.info(f"  Tarıyor: {ticker}")
        result = screen_ticker(ticker)
        if result:
            logger.info(f"  ✅ {ticker} — {len(result['signals'])} sinyal: {result['signals']}")
            candidates.append(result)
        else:
            logger.debug(f"  ❌ {ticker} — filtre geçemedi")

    logger.info(f"Screener tamamlandı: {len(candidates)} aday bulundu.")
    return candidates
