# ============================================================
#  modules/mail_sender.py  –  Gmail ile mail gönderici
# ============================================================

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config.settings import GMAIL_USER, GMAIL_PASSWORD, GMAIL_RECIPIENT

logger = logging.getLogger(__name__)


def send_opportunity_mail(candidates: list[dict], analysis: str) -> bool:
    """Fırsat radarı analizini Gmail ile gönderir."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"📊 Günlük Fırsat Raporu — {datetime.now().strftime('%d.%m.%Y')}"
        msg["From"]    = GMAIL_USER
        msg["To"]      = GMAIL_RECIPIENT

        # Düz metin
        ticker_list = ", ".join(c["ticker"] for c in candidates)
        plain = f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        plain += f"Adaylar: {ticker_list}\n\n"
        plain += analysis

        # HTML versiyon
        html_rows = ""
        for c in candidates:
            price  = c["data"]["price_data"]["price"]
            change = c["data"]["price_data"]["change_pct"]
            color  = "#c0392b" if change < 0 else "#27ae60"
            sinyaller = "<br>".join(c["signals"])
            html_rows += f"""
            <tr>
                <td><b>{c["ticker"]}</b></td>
                <td>{c["sector"]}</td>
                <td>${price}</td>
                <td style="color:{color}"><b>{change:+.2f}%</b></td>
                <td>{len(c["signals"])} sinyal</td>
                <td style="font-size:12px">{sinyaller}</td>
            </tr>"""

        html = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:800px;margin:auto">
        <h2>📊 Günlük Fırsat Raporu — {datetime.now().strftime('%d.%m.%Y')}</h2>

        <h3>🔍 Screener Adayları</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
            <tr style="background:#2c3e50;color:white">
                <th>Ticker</th><th>Sektör</th><th>Fiyat</th>
                <th>Değişim</th><th>Sinyal</th><th>Detay</th>
            </tr>
            {html_rows}
        </table>

        <h3>🤖 Gemini Analizi</h3>
        <pre style="background:#f8f9fa;padding:15px;border-radius:5px;white-space:pre-wrap">{analysis}</pre>

        <p style="color:#7f8c8d;font-size:12px">
            Stock Analyzer Bot — {datetime.now().strftime('%d.%m.%Y %H:%M')}
        </p>
        </body></html>
        """

        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 587) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, GMAIL_RECIPIENT, msg.as_string())

        logger.info(f"Fırsat raporu maili gönderildi: {GMAIL_RECIPIENT}")
        return True

    except Exception as e:
        logger.error(f"Mail gönderme hatası: {e}")
        return False