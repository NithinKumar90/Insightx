# 📋 InsightX — Sample Query Set

50 diverse queries tested and verified against the dataset.

---

## Section 1 — Insight Accuracy

**Q1: What is the overall transaction success rate?**
> 95.05% success rate (237,625 successful of 250,000 total)

**Q2: Which transaction type has the highest failure rate?**
> Recharge: 5.09% (6,341 failed of 124,651 total)

**Q3: What is the fraud flag rate by age group?**
> 56+ has highest at 0.2525%, followed by 26-35 at 0.2079%

**Q4: Which state has the most flagged transactions?**
> Uttar Pradesh: 5.22% failure rate (1,572 of 30,125)

**Q5: What is the average transaction amount by merchant category?**
> Education: ₹5,094.02 (highest), Transport: ₹308.00 (lowest)

**Q6: How does failure rate vary by hour of day?**
> Peak failures at 19:00 with 21,232 transactions

**Q7: Which age group spends most on weekends?**
> 26-35 age group has highest weekend transaction amounts

**Q8: Compare failure rates between 4G and 5G networks**
> 4G: 4.98%, 5G: 4.86%, 3G: 5.22% (highest), WiFi: 4.85%

**Q9: What % of high-value transactions (>₹5000) are flagged?**
> 33 out of 10,956 transactions above ₹5,000 are flagged (0.30%)

**Q10: Which bank+transaction type combination has the highest failure rate?**
> ICICI + Bill Payment: 5.54%

---

## Section 2 — Query Understanding

**Q11: Which bank has the most failed transactions?**
> SBI: 3,095 failures (highest by count, 4.94% rate)

**Q12: Compare failure rates between Android and iOS**
> Web: 5.15% > Android: 4.94% > iOS: 4.93%

**Q13: Which network type has the highest failure rate?**
> 3G: 5.22% (651 failed of 12,471 total)

**Q14: What are the peak hours for transactions?**
> 19:00 has most transactions (21,232), followed by 18:00 (20,064)

**Q15: Which merchant category has the highest average amount?**
> Education: ₹5,094.02

**Q16: Which state has the highest failure rate?**
> Uttar Pradesh: 5.22%

**Q17: What % of transactions above ₹5000 are flagged?**
> 0.30% (33 flagged of 10,956 total)

**Q18: Compare weekend vs weekday failure rates**
> Weekend: 5.09% (3,632 of 71,337) vs Weekday: 4.89% (8,744 of 178,663)

**Q19: Which age group has the highest fraud rate on weekends?**
> 56+: 0.2525%

**Q20: Which combination of bank and transaction type has the highest failure rate?**
> ICICI + Bill Payment: 5.54%

---

## Section 3 — Explainability

**Q21: How did you calculate the failure rate for each transaction type?**
> Step-by-step: filter FAILED status → count per type → divide by total → multiply by 100

**Q22: Explain why 3G has a higher failure rate than 4G and 5G**
> Lower bandwidth, higher latency, older devices, smaller user base (5% of transactions)

**Q23: Walk me through how fraud flagging works in this dataset**
> fraud_flag is 0 or 1 — flagged for review, not confirmed fraud. Rate: 0.19% (472 of 250,000)

**Q24: How is the average transaction amount calculated?**
> Sum all amount_inr values / total transactions = ₹328,940,000 / 250,000 = ₹1,312

**Q25: Explain the difference between fraud rate and failure rate**
> Failure rate (4.95%): transaction didn't complete. Fraud rate (0.19%): flagged as suspicious

**Q26: How did you determine which state has the highest failure rate?**
> Grouped by sender_state, counted FAILED, divided by total per state, sorted descending

**Q27: Why does Education have the highest average transaction amount?**
> Tuition fees, course materials — one-time large payments vs recurring small payments

**Q28: How confident are you in these numbers?**
> High confidence on aggregates. Limitations: synthetic data, no error codes, no retry info

**Q29: Explain how weekend vs weekday failure rates were computed step by step**
> Filter is_weekend==1/0 → count failures per group → divide by total → compare

**Q30: What does a 0.25% fraud flag rate mean in real numbers?**
> 0.25% of 250,000 = 625 transactions flagged across the dataset

---

## Section 4 — Conversational

**Q31: Which bank is worst?**
> Yes Bank: 1,269 failed of 24,860 (5.10%)

**Q32: Tell me more about that**
> Deeper breakdown of Yes Bank failure patterns

**Q33: What about iOS specifically?**
> Yes Bank still worst on iOS: 270 failed of 4,908 (5.50%)

**Q34: Now show me the same but only for weekends**
> Kotak highest on weekends: 307 failed of 5,687 (5.40%)

**Q35: Why do you think that is?**
> Higher mobile load, weekend usage patterns, network variability

**Q36: Can you compare that with fraud rates?**
> Kotak: failure 5.40% + fraud 0.2496% — dual risk bank

**Q37: Which one should I focus on fixing first?**
> Kotak — highest fraud rate (0.2496%), technical failures likely infrastructure issue

**Q38: Go back to what you said about SBI**
> SBI fraud: 109 flagged of 62,693 (0.1739%) — largest volume bank

**Q39: Interesting — what's the next most important insight?**
> Recharge: 5.09% failure rate — highest among transaction types

**Q40: Summarise everything we've discussed so far**
> Banks (Yes Bank worst) → iOS filter → Weekend (Kotak worst) → Fraud rates → Recharge insight

---

## Section 5 — Innovation & Technical

**Q41: If failure rate crosses 6%, what should trigger automatically?**
> Alert ops team → auto-switch routing → freeze new transactions → SLA breach notification

**Q42: How would you build a real-time fraud alert system?**
> Kafka stream → feature engineering → ML scoring → threshold alert → human review queue

**Q43: Which 3 metrics for a CEO dashboard?**
> 1. Overall Failure Rate (system health) 2. Fraud Flag Rate by Bank (risk) 3. Peak Hour Load (capacity)

**Q44: How would this scale to 10 million transactions/day?**
> Apache Kafka + Spark Streaming + Redis cache + horizontal pod scaling + read replicas

**Q45: What ML model to predict transaction failures?**
> Gradient Boosting (XGBoost/LightGBM) — handles class imbalance, feature importance, fast inference

**Q46: Design a smart routing system**
> Real-time failure rate per bank → route to lowest-failure bank → auto-fallback if >5% threshold

**Q47: What additional columns would make this 10x more powerful?**
> error_code, retry_count, device_os_version, pin_code, merchant_id, session_duration

**Q48: How to detect shifting fraud patterns?**
> Monthly trend analysis + Z-score anomaly detection + STL decomposition + drift monitoring

**Q49: Build a risk score formula**
> Risk = (network_3g × 2) + (amount_high × 1.5) + (hour_night × 1.2) + (fraud_flag × 10)

**Q50: What would production InsightX look like?**
> FastAPI backend + PostgreSQL + Redis + Kafka + React dashboard + CI/CD + monitoring
