import logging
import requests
import time

from config.settings import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    OPENAI_API_KEY
)

logger = logging.getLogger(__name__)


# ============================================================
# GEMINI
# ============================================================
class GeminiProvider:

    name = "gemini"

    URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
    )

    def ask(self, prompt: str) -> str:

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        resp = requests.post(
            self.URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30
        )

        # ❌ RETRY YOK — direkt fail / skip mantığı
        if resp.status_code == 429:
            raise Exception("RATE_LIMIT")

        if resp.status_code in [500, 502, 503, 504, 404]:
            raise Exception(f"SERVER_ERROR_{resp.status_code}")

        resp.raise_for_status()

        data = resp.json()

        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )


# ============================================================
# GROQ
# ============================================================
class GroqProvider:

    name = "groq"

    URL = "https://api.groq.com/openai/v1/chat/completions"

    def ask(self, prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        resp = requests.post(self.URL, headers=headers, json=payload, timeout=30)

        if resp.status_code in [429, 500, 502, 503, 504]:
            raise Exception(f"GROQ_ERROR_{resp.status_code}")

        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


# ============================================================
# OPENAI
# ============================================================
class OpenAIProvider:

    name = "openai"

    URL = "https://api.openai.com/v1/chat/completions"

    def ask(self, prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        resp = requests.post(self.URL, headers=headers, json=payload, timeout=30)

        if resp.status_code in [429, 500, 502, 503, 504]:
            raise Exception(f"OPENAI_ERROR_{resp.status_code}")

        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


# ============================================================
# AI MANAGER (SMART CIRCUIT BREAKER)
# ============================================================
class AIManager:

    def __init__(self):

        self.providers = [
            GeminiProvider(),
            GroqProvider(),
            OpenAIProvider()
        ]

        # 🧠 Gemini cooldown state
        self.cooldowns = {
            "gemini": 0
        }

        self.GEMINI_COOLDOWN_SEC = 300  # 5 dakika

    def analyze_news(self, prompt: str) -> str:

        now = time.time()
        last_error = None

        for provider in self.providers:

            # ====================================================
            # GEMINI COOLDOWN CHECK
            # ====================================================
            if provider.name == "gemini":
                if now < self.cooldowns["gemini"]:
                    logger.info("⏭️ Gemini cooldown active → skip")
                    continue

            start = time.time()

            try:
                logger.info(f"🤖 AI TRY: {provider.name}")

                result = provider.ask(prompt)

                duration = round(time.time() - start, 2)

                logger.info(f"✅ AI SUCCESS: {provider.name} ({duration}s)")

                return result

            except Exception as e:

                duration = round(time.time() - start, 2)

                msg = str(e)

                # ====================================================
                # GEMINI RATE LIMIT → COOLDOWN
                # ====================================================
                if provider.name == "gemini" and "RATE_LIMIT" in msg:
                    self.cooldowns["gemini"] = now + self.GEMINI_COOLDOWN_SEC
                    logger.warning("⛔ Gemini 5 dk devre dışı (429 rate limit)")
                    continue

                logger.warning(
                    f"❌ AI FAIL: {provider.name} ({duration}s) → {e}"
                )

                last_error = e
                continue

        raise Exception(f"Tüm AI servisleri başarısız: {last_error}")