# 💳 InsightX — UPI Payment Analytics Assistant

> An AI-powered conversational analytics dashboard for UPI transaction data, built for the Payment Intelligence Hackathon 2024.

---

## 🎯 What It Does

InsightX lets business leaders ask natural language questions about 250,000 UPI transactions and get instant, accurate insights — no SQL, no dashboards, no data science degree required.

**Example queries:**
- *"Which bank has the highest failure rate?"*
- *"Compare fraud rates by state"*
- *"What about iOS specifically?"*
- *"Summarise everything we've discussed"*

---

## 🏗️ System Architecture

```
User Query
    ↓
Smart Router (rule-based, ~50 patterns)
    ↓                    ↓
Pandas Code          LLM Reasoning
(data questions)     (explain/strategy)
    ↓                    ↓
Execute on DataFrame    Direct Answer
    ↓
Real Data Result
    ↓
LLM Insight Generator (Qwen 2.5 via LM Studio)
    ↓
Structured Response with Business Context
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) with **Qwen 2.5 7B Instruct** model loaded
- Git

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/insightx.git
cd insightx
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set up LM Studio
1. Download and open [LM Studio](https://lmstudio.ai/)
2. Search for `Qwen 2.5 7B Instruct` and download it
3. Go to **Local Server** tab → Start server on `http://localhost:1234`
4. Load the Qwen 2.5 model

### Step 4 — Add the dataset
Place the provided `upi_transactions_2024.csv` file in the root directory.

### Step 5 — Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📊 Dataset

- **Size:** 250,000 synthetic UPI transactions
- **Period:** 2024
- **Columns:** transaction_id, timestamp, transaction_type, merchant_category, amount_inr, transaction_status, sender_age_group, receiver_age_group, sender_state, sender_bank, receiver_bank, device_type, network_type, fraud_flag, hour_of_day, day_of_week, is_weekend

> ⚠️ Dataset is used as-is. No columns were removed or renamed. Derived features (filtering, aggregation) are computed at query time.

---

## 🧠 Key Technical Decisions

| Decision | Reasoning |
|----------|-----------|
| Smart Router (rule-based) | 50+ patterns give deterministic, accurate results for known query types |
| LM Studio (local LLM) | No API costs, privacy, works offline |
| Qwen 2.5 7B | Best balance of speed and quality for this hardware |
| Two-stage pipeline | Router → Pandas → LLM gives accuracy + natural language |
| Conversation history | Last 4 turns passed to LLM for follow-up handling |

---

## 👥 Team
Built during the Payment Intelligence Hackathon 2026
