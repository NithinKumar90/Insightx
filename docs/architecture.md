# 🏗️ InsightX — System Architecture

## Overview

InsightX uses a **two-stage pipeline**: a deterministic Smart Router for data questions, and an LLM for explanation and strategic questions.

---

## Pipeline Flow

```
1. USER INPUT
   "Which bank has the highest failure rate on weekends?"

2. QUERY PREPROCESSING
   expand_query() → resolves follow-ups using session context
   e.g. "same but weekends" → "failure rate by bank for weekend transactions"

3. MULTI-PART DETECTION
   split_multipart() → splits compound questions
   (follow-ups like "tell me more" are never split)

4. SMART ROUTER (route_query)
   50+ rule-based patterns match query intent
   Returns pandas code string if matched, None if not

5a. PANDAS EXECUTION (if router matched)
    execute_code() runs generated pandas on DataFrame
    Returns structured DataFrame result

5b. LLM CODE GENERATION (if router didn't match)
    generate_pandas_code() → LLM generates pandas
    execute_code() runs it

5c. DIRECT LLM (explain/strategy questions)
    "explain why", "how would you build", "design a" →
    Skip pandas entirely, LLM reasons from context

6. INSIGHT GENERATION
    generate_insight() → LLM converts data to business language
    Injects real pandas result into prompt
    Detects question type (data/explain/strategic)

7. RECOMMENDATIONS ENGINE
    get_recommendations() → rule-based actionable suggestions
    Based on query topic (failure/fraud/bank/network)

8. RESPONSE
    Structured output with emoji formatting
    Saved to conversation history for follow-ups
```

---

## Key Components

### Smart Router (50+ patterns)
Handles: failure rates, fraud rates, averages, counts, trends, bank comparisons, state analysis, device/network breakdown, age groups, merchant categories, weekend/weekday splits, iOS/Android filters, multi-dimensional combinations

### Context Engine
- `last_topic` stores expanded query (not raw input) for accurate follow-up resolution
- `last_result` stores last data output for comparison questions
- 4-turn conversation history passed to LLM

### Question Type Detection
- **Type A (Data):** runs pandas → LLM formats result
- **Type B (Explain):** runs pandas for real numbers → LLM explains methodology
- **Type C (Strategic):** skips pandas → LLM reasons from dataset context

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas 2.x |
| LLM | Qwen 2.5 7B via LM Studio |
| LLM API | OpenAI-compatible local endpoint |
| Language | Python 3.10+ |
| Storage | In-memory DataFrame + Streamlit session state |
