# 🧠 InsightX — Query Understanding & Insight Generation Approach

## The Core Problem

Business users ask questions in natural language. Data lives in a structured DataFrame. The gap between them is the hard part — especially when questions are vague ("tell me more"), contextual ("same but for iOS"), or multi-layered ("compare that with fraud rates").

---

## Our Approach: Hybrid Router + LLM

We rejected a pure LLM approach (hallucination risk) and a pure rule-based approach (too rigid). Instead we built a **hybrid two-stage system**:

### Stage 1: Smart Router
50+ deterministic pattern rules that map query intent to exact pandas code.

```python
# Example rule
if ("failure rate" in q or "fail" in q) and "bank" in q and "weekend" in q:
    return code(
        "wk = df[df['is_weekend']==1]",
        "failed = wk[wk['transaction_status']=='FAILED'].groupby('sender_bank').size()",
        "total  = wk.groupby('sender_bank').size()",
        "rate   = (failed / total * 100).round(2)",
        "result = pd.DataFrame(...).sort_values('Failure_Rate_%', ascending=False)"
    )
```

This guarantees **correct numbers** — the LLM never touches the calculation.

### Stage 2: LLM Insight Generator
The LLM receives the real pandas output and converts it to business language. It never calculates — it only interprets.

```
DATA (computed directly from 250,000 transactions):
Bank     Failed  Total  Failure_Rate_%
Kotak      307   5687          5.40
ICICI      443   8444          5.25
...

→ LLM: "Kotak has the highest weekend failure rate at 5.40%, which may indicate..."
```

---

## Query Understanding Techniques

### 1. Context-Aware Expansion
Short follow-ups are expanded using session history:
- "same but weekends" → "failure rate by bank for weekend transactions only"
- "what about iOS" → "compare failure rates by bank for iOS device type only"
- "tell me more" → "give me a deeper breakdown of: [last topic]"

### 2. Multi-Part Detection
Compound questions are split and answered individually:
- "Which bank is worst and which state is riskiest?" → two separate analyses

Conversational follow-ups are **never split** (e.g., "tell me more", "why do you think that").

### 3. Question Type Classification
Three types trigger different pipelines:
- **Type A (Data):** pandas → LLM formats
- **Type B (Explain):** pandas for numbers + LLM explains methodology
- **Type C (Strategic):** LLM reasons from dataset context, no pandas

### 4. Ambiguity Resolution
Vague queries trigger clarification or smart defaults:
- "compare banks" → shows all 8 banks by failure rate
- "tell me more" → deepens last topic with device/network/age breakdown

---

## Data Analysis Methodology

All calculations follow this pattern:
```python
# Failure rate
failed = df[df['transaction_status']=='FAILED'].groupby('COLUMN').size()
total  = df.groupby('COLUMN').size()
rate   = (failed / total * 100).round(2)
result = pd.DataFrame({...}).sort_values('Failure_Rate_%', ascending=False)

# Fraud rate  
tmp = df.groupby('COLUMN')['fraud_flag'].agg(['sum','count'])
tmp['Fraud_Rate_%'] = (tmp['sum'] / tmp['count'] * 100).round(4)
result = tmp.sort_values('Fraud_Rate_%', ascending=False).reset_index()
```

**Key principle:** First row always = highest value. LLM reads row 0 as its direct answer.

---

## Accuracy Safeguards

1. **No LLM calculation** — pandas does all math
2. **Strict data reading rules** in LLM prompt — "use ONLY numbers from the data"
3. **Exact column value injection** — "network_type values are EXACTLY: 4G, 5G, WiFi, 3G"
4. **Fraud vs failure distinction** — explicitly told: fraud rates < 1%, failure rates 4-6%
5. **Real counts always returned** — DataFrame with Failed/Total/Rate, never just a dict
