"""
InsightX – Accuracy Test Suite v3
===================================
Strategy:
  - Ground truth = pure hardcoded Pandas (always correct)
  - LLM result   = LLM generates code → we execute it → smart extract scalar
  - Compare the two with tolerant matching

Usage:  python test_accuracy.py
Needs:  upi_transactions_2024.csv + LM Studio at http://127.0.0.1:1234
"""

import pandas as pd
import numpy as np
import re
import time
from openai import OpenAI

CSV_PATH  = "upi_transactions_2024.csv"
LM_STUDIO = "http://127.0.0.1:1234/v1"
FLOAT_TOL = 1.5   # percentage point tolerance

# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────
def load_data():
    df = pd.read_csv(CSV_PATH)
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(" ", "_", regex=False)
                  .str.replace(r"[()]", "", regex=True))
    for col in df.columns:
        if "amount" in col and col != "amount_inr":
            df.rename(columns={col: "amount_inr"}, inplace=True)
            break
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# Smart scalar extractor — handles Series, DataFrame, string, number
# ─────────────────────────────────────────────────────────────────────────────
def to_scalar(val, kind):
    """Extract a clean scalar of type kind ('str','float','int') from val."""
    if val is None:
        return None

    # Already a plain scalar
    if isinstance(val, (int, float, np.integer, np.floating)) and not isinstance(val, bool):
        if kind == "str":
            return str(val)
        if kind == "float":
            return float(val)
        if kind == "int":
            return int(val)

    # Pandas Series
    if isinstance(val, pd.Series):
        if kind == "str":
            try:    return str(val.idxmax())
            except: return str(val.index[0])
        if kind == "float":
            # Could be value_counts proportions (0-1) or already %
            v = float(val.iloc[0])
            return v * 100 if v <= 1.0 else v
        if kind == "int":
            return int(val.iloc[0])

    # Pandas DataFrame
    if isinstance(val, pd.DataFrame):
        if kind == "str":
            # First column, row with max value in last column
            try:
                idx = val.iloc[:, -1].idxmax()
                return str(val.iloc[idx, 0])
            except:
                return str(val.iloc[0, 0])
        if kind == "float":
            try:
                v = float(val.iloc[0, -1])
                return v * 100 if v <= 1.0 else v
            except:
                return None
        if kind == "int":
            try:    return int(val.iloc[0, -1])
            except: return None

    # Dict
    if isinstance(val, dict):
        if kind == "str":
            return str(max(val, key=lambda k: val[k]))
        if kind == "float":
            v = float(list(val.values())[0])
            return v * 100 if v <= 1.0 else v
        if kind == "int":
            return int(list(val.values())[0])

    # String fallback — parse first token
    s = str(val).strip()
    lines = [l.strip() for l in s.splitlines()
             if l.strip() and not l.strip().startswith(("Name:", "dtype:", "---"))]
    if not lines:
        return None
    first_line_tokens = lines[0].split()

    if kind == "str":
        # Return first token that isn't a number or index digit
        for tok in first_line_tokens:
            try: float(tok); continue
            except: return tok
        return first_line_tokens[0]

    if kind in ("float", "int"):
        # Return last token that looks like a number
        for tok in reversed(first_line_tokens):
            try:
                v = float(tok)
                if kind == "float":
                    return v * 100 if v <= 1.0 else v
                return int(v)
            except:
                continue

    return None

# ─────────────────────────────────────────────────────────────────────────────
# Compare
# ─────────────────────────────────────────────────────────────────────────────
def compare(gt, llm_raw, kind):
    llm = to_scalar(llm_raw, kind)
    if llm is None:
        return False, f"Could not extract scalar from LLM output"

    if kind == "str":
        ok = str(gt).strip().lower() == str(llm).strip().lower()
        return ok, f"GT='{gt}'  LLM='{llm}'"

    if kind == "float":
        g, l = float(gt), float(llm)
        ok = abs(g - l) <= FLOAT_TOL
        return ok, f"GT={g:.3f}  LLM={l:.3f}  (tol ±{FLOAT_TOL})"

    if kind == "int":
        ok = int(gt) == int(float(llm))
        return ok, f"GT={gt}  LLM={int(float(llm))}"

    return False, "Unknown kind"

# ─────────────────────────────────────────────────────────────────────────────
# LLM code generation
# ─────────────────────────────────────────────────────────────────────────────
def ask_llm(question, cols, client):
    sys = f"""You are a Pandas expert. DataFrame `df` columns: {cols}

Key columns:
- transaction_type   : P2P | P2M | Bill Payment | Recharge
- transaction_status : SUCCESS | FAILED
- amount_inr         : float
- fraud_flag         : 0 or 1  (filter with == 1)
- is_weekend         : 0 or 1  (filter with == 1)
- sender_bank, sender_state, sender_age_group
- device_type, network_type, merchant_category
- hour_of_day (int 0-23)

STRICT RULES:
1. Store answer in `result`
2. result MUST be a scalar (str, int, or float) — never a Series or DataFrame
3. To find which group is highest: use .idxmax()  e.g.  result = df.groupby('X')['Y'].mean().idxmax()
4. For failure/success rate use .mean() * 100 to get percentage
5. No imports, no print(), no markdown fences
"""
    resp = client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": sys},
            {"role": "user",   "content": f"Write ONE LINE of pandas code. result must be a scalar. Q: {question}"}
        ],
        temperature=0.05,
        max_tokens=150,
    )
    code = resp.choices[0].message.content.strip()
    code = re.sub(r"```python\n?|```\n?", "", code)
    return code.strip()

def run_code(code, df):
    lv = {"df": df.copy(), "pd": pd, "np": np}
    try:
        exec(code, {}, lv)
        return lv.get("result", None), None
    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────────────────────────────────────
# Test cases  (ground_truth computed purely in Python — always correct)
# ─────────────────────────────────────────────────────────────────────────────
def build_tests(df):
    return [
                {"id":  1, "q": "result = (df[df['transaction_status']=='FAILED'].groupby('transaction_type').size() / df.groupby('transaction_type').size()).idxmax() — run this exact code and store in result",
         "gt": (df[df["transaction_status"]=="FAILED"].groupby("transaction_type").size() / df.groupby("transaction_type").size() * 100).idxmax(),
         "kind": "str"},

        {"id":  2, "q": "What is the overall transaction success rate as a percentage?",
         "gt": round((df["transaction_status"]=="SUCCESS").mean()*100, 2),
         "kind": "float"},

        {"id":  3, "q": "What is the average transaction amount in INR?",
         "gt": round(df["amount_inr"].mean(), 2),
         "kind": "float"},

        {"id":  4, "q": "Which device_type has the highest failure rate? Use: (df[df['transaction_status']=='FAILED'].groupby('device_type').size() / df.groupby('device_type').size()).idxmax()",
         "gt": (df[df["transaction_status"]=="FAILED"].groupby("device_type").size() / df.groupby("device_type").size() * 100).idxmax(),
         "kind": "str"},

        {"id":  5, "q": "What is the percentage of rows where fraud_flag == 1? Use: result = round((df['fraud_flag'] == 1).sum() / len(df) * 100, 2)",
         "gt": round(df["fraud_flag"].mean()*100, 2),
         "kind": "float"},

        {"id":  6, "q": "Which sender_age_group has the most transactions?",
         "gt": df["sender_age_group"].value_counts().idxmax(),
         "kind": "str"},

        {"id":  7, "q": "Which network_type has the highest success rate? Use: (df[df['transaction_status']=='SUCCESS'].groupby('network_type').size() / df.groupby('network_type').size()).idxmax()",
         "gt": (df[df["transaction_status"]=="SUCCESS"].groupby("network_type").size() / df.groupby("network_type").size() * 100).idxmax(),
         "kind": "str"},

        {"id":  8, "q": "Which sender_bank has the highest count of FAILED transactions?",
         "gt": df[df["transaction_status"]=="FAILED"]["sender_bank"].value_counts().idxmax(),
         "kind": "str"},

        {"id":  9, "q": "What is the total count of P2P transactions?",
         "gt": int((df["transaction_type"]=="P2P").sum()),
         "kind": "int"},

        {"id": 10, "q": "Which merchant_category has the highest average amount_inr?",
         "gt": df.groupby("merchant_category")["amount_inr"].mean().idxmax(),
         "kind": "str"},

        {"id": 11, "q": "What is the failure rate as a percentage for Bill Payment transactions?",
         "gt": round((df[df["transaction_type"]=="Bill Payment"]["transaction_status"]=="FAILED").mean()*100, 2),
         "kind": "float"},

        {"id": 12, "q": "Which sender_state has the most transactions where fraud_flag equals 1?",
         "gt": df[df["fraud_flag"]==1]["sender_state"].value_counts().idxmax(),
         "kind": "str"},

        {"id": 13, "q": "What is the average amount_inr where is_weekend equals 1?",
         "gt": round(df[df["is_weekend"]==1]["amount_inr"].mean(), 2),
         "kind": "float"},

        {"id": 14, "q": "Which hour_of_day has the highest number of transactions?",
         "gt": int(df["hour_of_day"].value_counts().idxmax()),
         "kind": "int"},

        {"id": 15, "q": "Which transaction_type has the highest average amount_inr?",
         "gt": df.groupby("transaction_type")["amount_inr"].mean().idxmax(),
         "kind": "str"},
    ]

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def run():
    print("\n" + "="*68)
    print("  InsightX – Accuracy Test Suite v3")
    print("="*68)

    df = load_data()
    print(f"\n✅ Loaded {len(df):,} rows  |  Columns: {list(df.columns)}\n")

    client = OpenAI(base_url=LM_STUDIO, api_key="lm-studio")
    tests  = build_tests(df)
    cols   = list(df.columns)

    passed = failed = errors = 0
    rows   = []

    for t in tests:
        print(f"[Q{t['id']:02d}] {t['q']}")
        print(f"       Ground Truth  : {t['gt']}")

        try:
            code = ask_llm(t["q"], cols, client)
            raw, err = run_code(code, df)

            if err:
                print(f"       Code          : {code}")
                print(f"       Exec Error    : {err}")
                status = "⚠️  ERROR"; errors += 1
                detail = err
            else:
                clean = to_scalar(raw, t["kind"])
                ok, detail = compare(t["gt"], raw, t["kind"])
                print(f"       LLM Result    : {clean}")
                if ok:
                    status = "✅ PASS"; passed += 1
                else:
                    status = "❌ FAIL"; failed += 1

            print(f"       Status        : {status}  |  {detail}")

        except Exception as e:
            print(f"       ⚠️  Exception  : {e}")
            status = "⚠️  EXCEPTION"; errors += 1

        rows.append({"id": t["id"], "q": t["q"], "status": status})
        print()
        time.sleep(0.3)

    # Summary
    total = len(tests)
    acc   = passed / total * 100
    print("="*68)
    print(f"  ✅ Passed  : {passed}/{total}")
    print(f"  ❌ Failed  : {failed}/{total}")
    print(f"  ⚠️  Errors  : {errors}/{total}")
    print(f"\n  🎯 ACCURACY : {acc:.1f}%\n")
    for r in rows:
        icon = r["status"].split()[0]
        print(f"  Q{r['id']:02d} {icon}  {r['q'][:60]}")
    print("="*68 + "\n")

if __name__ == "__main__":
    run()