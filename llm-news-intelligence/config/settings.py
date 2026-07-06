# ============================================================
#  config/settings.py  –  Tüm API anahtarları ve ayarlar
# ============================================================

# --- Takip etmek istediğin hisseler ---
WATCHLIST = [
    "ORCL",  
    "NVDA",  
    "MSFT",   
    "MSTR",  
    "SOUN",  
    "VERI"
]

# --- API Anahtarları ---
NEWSAPI_KEY     = "************"        # https://newsapi.org
GEMINI_API_KEY  = "************"     # https://aistudio.google.com
PUSHOVER_TOKEN  = "************" # https://pushover.net
PUSHOVER_USER   = "************"
FINNHUB_API_KEY = "************"    # https://finnhub.io/register (ücretsiz)
GROQ_API_KEY="************
OPENAI_API_KEY="************"
GMAIL_USER      = "************"
GMAIL_PASSWORD  = "************"
GMAIL_RECIPIENT = "************"
# --- Teknik İndikatör Parametreleri ---
RSI_PERIOD          = 14
MACD_FAST           = 12
MACD_SLOW           = 26
MACD_SIGNAL         = 9
BB_PERIOD           = 20
BB_STD              = 2
SMA_PERIODS         = [20, 50, 200]   # Kısa, Orta, Uzun vadeli MA
EMA_PERIODS         = [9, 21]
ATR_PERIOD          = 14
TREND_BASE_PERIOD   = 20

# --- Veri ayarları ---
YFINANCE_PERIOD     = "1y"    # Yeterli geçmiş veri için 3 ay
YFINANCE_INTERVAL   = "1d"
NEWS_ARTICLE_COUNT  = 5
NEWS_MAX_AGE_DAYS = 7  # Son 1 haftanın haberleri


# --- Pushover bildirim önceliği (-2 sessiz → 2 acil) ---
PUSHOVER_PRIORITY   = 0

# --- Piyasa saatleri (sadece bu saatler arasında çalış) ---
# NYSE: 09:30–16:00 ET → UTC 14:30–21:00
MARKET_OPEN_HOUR_UTC  = 12
MARKET_CLOSE_HOUR_UTC = 20
RUN_ONLY_MARKET_HOURS = True   # False yaparak 7/24 çalıştırabilirsin
