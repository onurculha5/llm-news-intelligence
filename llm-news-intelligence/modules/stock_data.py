# ============================================================
#  modules/stock_data.py  –  yfinance + Teknik İndikatörler
# ============================================================

import logging
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from config.settings import (
    YFINANCE_PERIOD, YFINANCE_INTERVAL,
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, SMA_PERIODS, EMA_PERIODS
)

logger = logging.getLogger(__name__)


def fetch_stock_data(ticker: str) -> pd.DataFrame | None:
    """yfinance'dan OHLCV verisi çeker."""
    try:
        df = yf.download(
            ticker,
            period=YFINANCE_INTERVAL and YFINANCE_PERIOD,
            interval=YFINANCE_INTERVAL,
            progress=False,
            auto_adjust=True
        )
        if df.empty:
            logger.warning(f"{ticker}: Veri bulunamadı.")
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception as e:
        logger.error(f"{ticker} verisi çekilirken hata: {e}")
        return None


def calculate_indicators(df: pd.DataFrame) -> dict:
    """Tüm teknik indikatörleri hesaplar ve son değerleri döner."""
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]

    indicators = {}

    # --- RSI ---
    rsi = ta.rsi(close, length=RSI_PERIOD)
    indicators["RSI"] = round(float(rsi.iloc[-1]), 2) if rsi is not None else None

    # --- MACD ---
    macd_df = ta.macd(close, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    if macd_df is not None:
        indicators["MACD"]        = round(float(macd_df.iloc[-1, 0]), 4)
        indicators["MACD_Signal"] = round(float(macd_df.iloc[-1, 2]), 4)
        indicators["MACD_Hist"]   = round(float(macd_df.iloc[-1, 1]), 4)

    # --- Bollinger Bands ---
    bb = ta.bbands(close, length=BB_PERIOD, std=BB_STD)
    if bb is not None:
        indicators["BB_Upper"]  = round(float(bb.iloc[-1, 0]), 2)
        indicators["BB_Mid"]    = round(float(bb.iloc[-1, 1]), 2)
        indicators["BB_Lower"]  = round(float(bb.iloc[-1, 2]), 2)
        indicators["BB_Width"]  = round(float(bb.iloc[-1, 3]), 4)

    # --- SMA ---
    for period in SMA_PERIODS:
        sma = ta.sma(close, length=period)
        if sma is not None:
            indicators[f"SMA_{period}"] = round(float(sma.iloc[-1]), 2)

    # --- EMA ---
    for period in EMA_PERIODS:
        ema = ta.ema(close, length=period)
        if ema is not None:
            indicators[f"EMA_{period}"] = round(float(ema.iloc[-1]), 2)

    # --- ATR (Volatilite) ---
    atr = ta.atr(high, low, close, length=14)
    if atr is not None:
        indicators["ATR_14"] = round(float(atr.iloc[-1]), 4)

    # --- Stochastic Oscillator ---
    stoch = ta.stoch(high, low, close)
    if stoch is not None:
        indicators["Stoch_K"] = round(float(stoch.iloc[-1, 0]), 2)
        indicators["Stoch_D"] = round(float(stoch.iloc[-1, 1]), 2)

    # --- OBV (On-Balance Volume) ---
    obv = ta.obv(close, df["Volume"])
    if obv is not None:
        indicators["OBV"] = int(obv.iloc[-1])

    return indicators


def get_price_summary(df: pd.DataFrame) -> dict:
    """Son fiyat bilgilerini özetler."""
    last  = df.iloc[-1]
    prev  = df.iloc[-2]
    change_pct = ((float(last["Close"]) - float(prev["Close"])) / float(prev["Close"])) * 100

    return {
        "price":      round(float(last["Close"]), 2),
        "open":       round(float(last["Open"]), 2),
        "high":       round(float(last["High"]), 2),
        "low":        round(float(last["Low"]), 2),
        "volume":     int(last["Volume"]),
        "change_pct": round(change_pct, 2),
    }


def analyze_ticker(ticker: str) -> dict | None:
    """Bir hisse için tüm veri ve indikatörleri toplar."""
    df = fetch_stock_data(ticker)
    if df is None or len(df) < 50:
        return None

    price   = get_price_summary(df)
    indics  = calculate_indicators(df)

    return {
        "ticker":     ticker,
        "price_data": price,
        "indicators": indics,
    }
