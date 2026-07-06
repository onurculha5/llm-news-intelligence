# 🚀 LLM News Intelligence

> AI-powered financial news intelligence platform with multi-provider LLM orchestration, automatic failover, sentiment analysis, and opportunity detection.

---

## 📌 Overview

LLM News Intelligence is an AI-driven platform that collects financial news, analyzes market sentiment using multiple Large Language Models (LLMs), and generates actionable insights for stock investors.

Instead of relying on a single AI provider, the platform automatically routes requests through multiple LLMs (Google Gemini, Groq, OpenAI). If one provider becomes unavailable or reaches its rate limit, the system seamlessly switches to another provider without interrupting the analysis.

This architecture ensures high availability, resilience, and consistent AI-powered market analysis.

---

## ✨ Key Features

- 🤖 Multi-LLM Architecture
- 🔄 Automatic Provider Failover
- 🛡 Smart Circuit Breaker (Rate Limit Protection)
- 📰 Financial News Collection
- 📊 AI-Based News Analysis
- 📈 Stock Opportunity Detection
- 📧 Email Notifications
- 📝 Notebook Logging
- ⚙️ Configurable Watchlists
- ⏰ Automated Hourly Execution

---

## 🏗 Architecture

```
                Financial News APIs
                         │
                         ▼
                News Collection Layer
                         │
                         ▼
                 Prompt Builder
                         │
                         ▼
                    AI Manager
                         │
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
  Google Gemini        Groq              OpenAI
      │                  │                  │
      └────────── Automatic Failover ───────┘
                         │
                         ▼
              AI Market Intelligence
                         │
                         ▼
          Email Alerts / Reports / Notebook
```

---

## 🧠 Multi-LLM Orchestration

The platform uses a centralized **AI Manager** responsible for:

- Selecting the active LLM provider
- Detecting provider failures
- Handling API rate limits
- Applying cooldown policies
- Automatically switching to the next available provider
- Returning a unified response regardless of provider

Supported providers:

- Google Gemini
- Groq (Llama 3.3 70B)
- OpenAI GPT-4.1 Mini

---

## 🔄 Automatic Failover

Example execution flow:

```
Gemini
   │
429 Rate Limit
   │
Cooldown (5 min)
   │
   ▼
Groq
   │
Success
   │
   ▼
Application continues normally
```

The application never depends on a single AI provider.

---

## 📈 Project Workflow

```
Watchlist

     │

     ▼

Stock Analysis

     │

     ▼

Financial News Collection

     │

     ▼

Prompt Generation

     │

     ▼

AI Manager

     │

     ▼

Market Analysis

     │

     ▼

Email Notification
```

---

## 🛠 Technology Stack

- Python
- OpenAI API
- Google Gemini API
- Groq API
- Finnhub API
- Requests
- Logging
- REST APIs

---

## 📂 Project Structure

```
llm-news-intelligence/

├── config/
├── modules/
├── logs/
├── main.py
├── requirements.txt
└── README.md
```

---

## 🎯 Future Improvements

- Claude support
- Mistral support
- Local LLM support (Ollama)
- Docker deployment
- FastAPI REST interface
- Web dashboard
- AI Agent workflow
- Portfolio optimization

---

## 👨‍💻 Author

Developed by **Onur Çulha**

Passionate about AI-powered financial intelligence, LLM orchestration, product development, and intelligent automation.
