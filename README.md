# 🚀 LLM News Intelligence

<p align="center">

AI-powered financial market intelligence platform built with multiple Large Language Models.

Automatically monitors stocks, collects financial news, performs AI-driven analysis, identifies investment opportunities, and sends real-time notifications.

</p>

---

## 📌 Overview

LLM News Intelligence is an autonomous market analysis platform that combines:

- 📈 Real-time stock market data
- 📰 Financial news aggregation
- 📊 Technical indicators
- 🤖 Multiple AI providers
- 📲 Instant mobile notifications
- 📧 Daily opportunity reports

Instead of manually reading dozens of news articles every day, the platform continuously analyzes your watchlist and delivers concise investment insights.

---

# 🏗 System Architecture

```text
                        ┌────────────────────────────┐
                        │      Scheduled Runner      │
                        │     (Runs Every Hour)      │
                        └──────────────┬─────────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
          Watchlist Analysis                    Market Screener
                     │                                   │
                     ▼                                   ▼
             Stock Data API                    Stock Screening
                     │                                   │
                     ▼                                   ▼
          Technical Indicators                 Candidate Stocks
                     │                                   │
                     └──────────────┬────────────────────┘
                                    ▼
                          Financial News Fetcher
                                    │
                                    ▼
                           Prompt Builder
                                    │
                                    ▼
                              AI Manager
                                    │
      ┌───────────────┬──────────────┬───────────────┐
      ▼               ▼              ▼
 Google Gemini     Groq AI       OpenAI GPT
      │               │              │
      └──────── Automatic Failover ─────────┘
                     │
                     ▼
             AI Investment Analysis
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
  📲 Pushover Alerts      📧 Email Reports
```

---

# ✨ Features

## 📈 Watchlist Monitoring

Monitor your favorite stocks automatically.

Features:

- Hourly execution
- Technical analysis
- Financial news collection
- AI-powered interpretation
- Mobile notifications

---

## 📊 Technical Analysis

For every stock the platform calculates:

- RSI
- MACD
- Bollinger Bands
- ATR
- SMA 20 / 50 / 200
- Stochastic Oscillator
- Daily price change
- Volume analysis

---

## 📰 Financial News Intelligence

Latest financial news is collected and combined with technical indicators.

Instead of simply summarizing news, the AI evaluates:

- Market sentiment
- Technical trend
- News impact
- Risk level
- Investment signal

---

# 🤖 Multi-LLM Architecture

The platform is completely model-agnostic.

Supported providers:

| Provider | Purpose |
|----------|---------|
| Google Gemini | Primary |
| Groq (Llama 3.3 70B) | Automatic fallback |
| OpenAI GPT-4.1 Mini | Final fallback |

---

## Smart AI Routing

```text
                AI Request

                     │

                     ▼

               AI Manager

                     │

          ┌──────────┼───────────┐

          ▼          ▼           ▼

      Gemini      Groq      OpenAI

          │

      Rate Limit?

          │

      Yes ▼

    5 min Cooldown

          │

          ▼

   Automatically switch

      to next provider
```

No manual intervention is required.

The application never depends on a single AI provider.

---

# 📲 Notification System

The platform uses two different notification channels.

## Instant Mobile Alerts

Pushover notifications are sent when:

- Buy signals appear
- Sell signals appear
- Watchlist stocks change significantly
- Important news is detected

Example:

```text
🟢 AAPL

SIGNAL : BUY

Confidence : High

RSI indicates oversold conditions while recent news remains positive.

Watch : $205 support level
```

---

## Daily Opportunity Report

Every day the screener scans the market and sends an email containing:

- Best opportunities
- AI summaries
- Risk evaluation
- Investment signals

---

# 🔄 AI Failover

```text
Gemini

   │

429 Rate Limit

   │

Cooldown

   │

   ▼

Groq

   │

Success

   │

   ▼

Application continues
```

If one provider becomes unavailable the system automatically switches to another provider.

---

# ⚙ Workflow

```text
Every Hour

     │

     ▼

Download Stock Data

     │

     ▼

Calculate Technical Indicators

     │

     ▼

Collect Financial News

     │

     ▼

Build AI Prompt

     │

     ▼

Multi-LLM Analysis

     │

     ▼

Generate Investment Insight

     │

     ▼

Send Notification
```

---

# 🛠 Technology Stack

- Python
- Google Gemini API
- OpenAI API
- Groq API
- Finnhub API
- Requests
- Pandas
- Logging
- Pushover API
- SMTP Email
- REST APIs

---

# 📂 Project Structure

```text
llm-news-intelligence/

│
├── config/
│
├── modules/
│   ├── ai_manager.py
│   ├── prompt_builder.py
│   ├── news_fetcher.py
│   ├── stock_data.py
│   ├── screener.py
│   ├── notifier.py
│   └── opportunity_analyzer.py
│
├── logs/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# 🚀 Roadmap

- Claude integration
- Mistral integration
- Local LLM (Ollama)
- Docker deployment
- FastAPI interface
- Web dashboard
- Portfolio optimization
- AI Agent workflows
- Vector database integration

---

# 👨‍💻 About

Developed by **Onur Çulha**

Business Analyst & AI Product enthusiast focused on:

- Multi-LLM systems
- AI Agents
- Financial Intelligence
- Product Development
- Intelligent Automation
