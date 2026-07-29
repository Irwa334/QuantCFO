# 🪙 QuantCFO — AI-Powered Financial Analytics Platform

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)
![Pandas](https://img.shields.io/badge/Pandas-Data_Engineering-150458)
![AI](https://img.shields.io/badge/AI-Llama_3.1-04A77B)

---

## Overview
**App Name:** QuantCFO  
**What it does:** QuantCFO is an AI-powered financial intelligence dashboard that transforms raw financial transactions into interactive analytics, automated insights, and conversational business intelligence. Users can upload messy CSV files, explore dashboards, ask natural-language questions, and run budget simulations—all in one application.

**The Real Problem It Solves:** Small businesses, startups, and freelancers frequently struggle with messy, unstandardized financial data exported from various bank accounts. Manually calculating cash flow, categorizing mixed expenses, and forecasting budgets is tedious, error-prone, and time-consuming. QuantCFO solves this by automating the data cleaning (ETL) pipeline, visualizing performance metrics in real-time, and delivering high-level financial consulting without the high cost of a human analyst.

---

## Highlights
- End-to-end AI web application
- Interactive financial dashboards
- LLM integration using Llama 3.1
- Automated ETL pipeline
- Cloud deployment
- Natural-language financial analysis
- Responsive Streamlit interface

---

## Live Deployed URL
🔗 **Access the Live Application Here:** https://quantcfo-sa8ldag6fnnkdgvc3heg6p.streamlit.app/

*(Note: The live deployed version on Streamlit Community Cloud has a platform-enforced hard limit of 200MB for CSV file uploads. When run locally, this limit is extended up to 1GB.)*

---

## Screenshots of the App in Action
**Executive Overview & Visual Analytics Dashboard:**
*(Displays real-time KPIs, expense distribution breakdown, and revenue vs. expense comparisons)*
![Executive Overview Dashboard](Executive Overview Dashboard.png)

**Deep Dive Analytics & Expense Distribution:**
*(Highlights top transactions and categorized cost breakdowns)*
![Deep Dive Analytics and Expense Distribution](analytics_screenshot.png)

**AI Financial Advisor & Chat Suite (Core Feature):**
*(Shows the instant CFO report, natural language chat, and what-if simulation engine)*
![AI Financial Advisor and Chat Suite](ai_chat_screenshot.png)

**Transaction Ledger & Data Export:**
*(The standardized table view resulting from the Smart Schema Adapter)*
![Transaction Ledger and Data Export](ledger_screenshot.png)

---

## Features

**Data Processing**
- Smart schema detection
- Automatic data cleaning
- Currency support

**Analytics**
- KPI dashboard
- Cash-flow summaries
- Interactive charts

**AI Features**
- Financial audit
- AI chat
- What-if simulations

**Export**
- Clean ledger
- CSV download

---

## Project Architecture Flow
```text
CSV Upload
      │
      ▼
Smart ETL Pipeline
      │
      ▼
Data Cleaning & Standardisation
      │
      ▼
Financial Analytics Engine
      │
 ┌────┴────────────┐
 ▼                 ▼
Dashboard       AI Engine
(Plotly)    (Pandas + Llama 3.1)
      │
      ▼
Interactive Reports
      │
      ▼
Export & Insights
```

---

## The AI Feature & System Instructions
QuantCFO integrates Meta's Llama 3.1 (8b-instant) model via the Groq API to provide AI-powered financial intelligence.

I engineered a custom **Context Compression Strategy** to overcome common Large Language Model limitations. To eliminate math hallucinations, all financial summaries and category totals are deterministically computed with Pandas *before* being injected into the LLM prompt context. The AI is explicitly instructed to rely on these pre-calculated totals rather than attempting math on raw transactions. 

Additionally, the system aggregates repetitive transactions and strictly filters for the Top 100 most financially impactful records before querying the AI. This guarantees the application stays well under strict free-tier API token limits (HTTP 413) while preserving 100% accurate top-level financial insights.

---

## Technology Stack & Services Used
- **Frontend & UI Framework:** Streamlit
- **Data Processing & Engineering:** Pandas
- **Data Visualization:** Plotly Express
- **AI Model Provider:** Groq API (Llama-3.1-8b-instant)
- **Hosting / Deployment:** Streamlit Community Cloud

---

## How to Run the Project Locally
Follow these instructions to set up and run QuantCFO on your local machine:

1. Clone the repository:
```bash
git clone https://github.com/lrwa334/QuantCFO.git
cd QuantCFO
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly groq
```

3. Configure your API Keys (Secure Secrets):
Create a hidden folder named `.streamlit` in the project root directory.
Inside that folder, create a file named `secrets.toml`.
Add your Groq API key:
```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```
*(⚠️ Never commit your `secrets.toml` file or API keys to GitHub!)*

4. Run the application:
```bash
streamlit run app.py
```

---

## My Contributions
- Designed the complete system architecture
- Built the ETL pipeline
- Engineered the financial analytics engine
- Integrated Groq Llama 3.1
- Developed the Streamlit frontend
- Designed AI prompts and context-compression strategy
- Deployed the application to Streamlit Community Cloud

*Designed and developed independently as a full-stack AI-powered financial analytics application.*
