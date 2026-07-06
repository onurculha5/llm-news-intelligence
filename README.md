# 🚀 LLM News Intelligence

> An AI-powered market intelligence platform that continuously monitors your watchlist, analyzes financial news with multiple LLM providers, identifies trading opportunities, and delivers real-time alerts.

---

## Why I Built This

Monitoring dozens of stocks and reading financial news every hour is both time-consuming and inefficient.

LLM News Intelligence automates this entire workflow by combining:

- Real-time stock data
- Financial news
- Technical indicators
- Large Language Models (LLMs)

The platform continuously analyzes market conditions and delivers concise, actionable insights instead of raw information.

---

## Features

### 📈 Watchlist Monitoring

Monitor your favorite stocks automatically.

- Configurable watchlist
- Hourly execution
- Technical indicator analysis
- News aggregation
- AI-powered interpretation

---

### 🧠 AI Market Analysis

Instead of simple sentiment analysis, the platform combines:

- Technical indicators
- Price action
- Recent financial news
- Market context

to generate a concise investment summary.

---

### 🤖 Multi-LLM Intelligence

The platform is model-agnostic.

Supported providers:

- Google Gemini
- OpenAI
- Groq (Llama 3.3)

If one provider becomes unavailable, another provider automatically continues the analysis.

No manual intervention required.

---

### 🚨 Smart Notifications

Two different notification channels are used depending on the analysis type.

#### 📲 Pushover

Instant mobile notifications for:

- Watchlist updates
- Buy/Sell signals
- Important market events

#### 📧 Email Reports

Daily opportunity reports containing:

- Top screened stocks
- AI-generated summaries
- Potential trading opportunities

---

### 🔄 Automatic Failover

The AI Manager automatically:

- Detects API failures
- Detects rate limits
- Applies cooldown policies
- Switches to another LLM provider

ensuring uninterrupted market analysis.
