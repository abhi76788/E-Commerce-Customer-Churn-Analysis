"""
churn_analysis.py
=================
Analyse churned vs. active customer behaviour and identify churn indicators.

Reads:
    data/processed/customer_features.csv

Outputs:
    - Printed KPI summary to stdout
    - data/processed/churn_summary.csv   (per-segment churn stats)
"""

import os
import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FEATURES_CSV  = os.path.join(PROCESSED_DIR, "customer_features.csv")


# ── 1. Load Features ─────────────────────────────────────────────────────────
def load_features() -> pd.DataFrame:
    """Load the pre-built customer feature table."""
    if not os.path.exists(FEATURES_CSV):
        raise FileNotFoundError(
            f"{FEATURES_CSV} not found. "
            "Run data_preprocessing.py first."
        )
    df = pd.read_csv(FEATURES_CSV, parse_dates=["signup_date", "last_purchase_date"])
    print(f"Loaded {len(df):,} customers with {len(df.columns)} features.")
    return df


# ── 2. Overall KPIs ──────────────────────────────────────────────────────────
def compute_overall_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of headline KPI values."""
    active  = df[df["is_churned"] == 0]
    churned = df[df["is_churned"] == 1]

    kpis = {
        "total_customers":        len(df),
        "active_customers":       len(active),
        "churned_customers":      len(churned),
        "churn_rate_pct":         round(len(churned) / len(df) * 100, 2),
        "overall_aov":            round(df["avg_order_value"].mean(), 2),
        "active_aov":             round(active["avg_order_value"].mean(), 2),
        "churned_aov":            round(churned["avg_order_value"].mean(), 2),
        "repeat_purchase_rate":   round((df["frequency"] > 1).mean() * 100, 2),
        "avg_clv_active":         round(active["monetary"].mean(), 2),
        "avg_clv_churned":        round(churned["monetary"].mean(), 2),
        "avg_recency_active":     round(active["recency_days"].mean(), 1),
        "avg_recency_churned":    round(churned["recency_days"].mean(), 1),
        "avg_frequency_active":   round(active["frequency"].mean(), 2),
        "avg_frequency_churned":  round(churned["frequency"].mean(), 2),
    }
    return kpis


def print_kpis(kpis: dict) -> None:
    print("\n" + "=" * 55)
    print("  E-COMMERCE CHURN ANALYSIS — KEY METRICS")
    print("=" * 55)
    print(f"  Total customers        : {kpis['total_customers']:,}")
    print(f"  Active customers       : {kpis['active_customers']:,}")
    print(f"  Churned customers      : {kpis['churned_customers']:,}")
    print(f"  Overall churn rate     : {kpis['churn_rate_pct']}%")
    print(f"  Repeat purchase rate   : {kpis['repeat_purchase_rate']}%")
    print(f"  Average CLV (active)   : ${kpis['avg_clv_active']:,.2f}")
    print(f"  Average CLV (churned)  : ${kpis['avg_clv_churned']:,.2f}")
    print(f"  AOV – active           : ${kpis['active_aov']:,.2f}")
    print(f"  AOV – churned          : ${kpis['churned_aov']:,.2f}")
    print(f"  Avg recency – active   : {kpis['avg_recency_active']} days")
    print(f"  Avg recency – churned  : {kpis['avg_recency_churned']} days")
    print(f"  Avg frequency – active : {kpis['avg_frequency_active']} orders")
    print(f"  Avg frequency – churned: {kpis['avg_frequency_churned']} orders")
    print("=" * 55 + "\n")


# ── 3. Churn Rate by Segment ─────────────────────────────────────────────────
def churn_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Compute churn rate and mean metrics per original segment."""
    grp = df.groupby("segment").agg(
        total_customers=("customer_id", "count"),
        churned=("is_churned", "sum"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_order_value=("avg_order_value", "mean"),
    ).reset_index()

    grp["active"]        = grp["total_customers"] - grp["churned"]
    grp["churn_rate_pct"] = (grp["churned"] / grp["total_customers"] * 100).round(2)
    grp = grp.sort_values("churn_rate_pct", ascending=False).reset_index(drop=True)

    for col in ["avg_recency", "avg_frequency", "avg_monetary", "avg_order_value"]:
        grp[col] = grp[col].round(2)

    print("\nChurn Rate by Customer Segment:")
    print(grp[["segment", "total_customers", "churned", "active",
                "churn_rate_pct", "avg_recency", "avg_frequency"]].to_string(index=False))
    return grp


# ── 4. Churn by Product Category ─────────────────────────────────────────────
def churn_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Identify churn patterns by preferred product category."""
    grp = df.groupby("preferred_category").agg(
        total_customers=("customer_id", "count"),
        churned=("is_churned", "sum"),
        avg_order_value=("avg_order_value", "mean"),
    ).reset_index()
    grp["churn_rate_pct"] = (grp["churned"] / grp["total_customers"] * 100).round(2)
    grp = grp.sort_values("churn_rate_pct", ascending=False).reset_index(drop=True)

    print("\nChurn Rate by Preferred Product Category:")
    print(grp.to_string(index=False))
    return grp


# ── 5. High-Risk Customer Identification ──────────────────────────────────────
def identify_high_risk(df: pd.DataFrame,
                        min_days: int = 60,
                        max_days: int = 90) -> pd.DataFrame:
    """
    Return customers in the pre-churn window (60–90 days inactive).
    These are the primary targets for re-engagement campaigns.
    """
    at_risk = df[
        (df["recency_days"] >= min_days) &
        (df["recency_days"] <= max_days) &
        (df["is_churned"] == 0)
    ].copy()

    at_risk = at_risk.sort_values("monetary", ascending=False).reset_index(drop=True)
    print(f"\nHigh-Risk Customers (60–90 days inactive): {len(at_risk):,}")
    if len(at_risk) > 0:
        print(at_risk[["customer_id", "name", "segment", "recency_days",
                        "frequency", "monetary"]].head(10).to_string(index=False))
    return at_risk


# ── 6. Churn Indicators (Feature Importance via Correlation) ──────────────────
def churn_indicators(df: pd.DataFrame) -> pd.Series:
    """
    Compute point-biserial correlation of numeric features with churn label.
    Higher absolute value = stronger churn predictor.
    """
    numeric_cols = [
        "recency_days", "frequency", "monetary", "avg_order_value",
        "max_order_value", "num_categories", "discount_order_rate",
        "return_rate", "customer_age_days", "avg_days_between_orders",
    ]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available + ["is_churned"]].corr()["is_churned"].drop("is_churned")
    corr = corr.abs().sort_values(ascending=False)

    print("\nTop Churn Indicators (absolute correlation with churn):")
    print(corr.round(4).to_string())
    return corr


# ── 7. Monthly Churn Trend (from transactions) ───────────────────────────────
def monthly_churn_trend(transactions_csv: str) -> pd.DataFrame:
    """
    Approximate monthly churn: customers active in month M but not M+1.
    """
    if not os.path.exists(transactions_csv):
        print("Transactions file not found; skipping monthly trend.")
        return pd.DataFrame()

    df = pd.read_csv(transactions_csv, parse_dates=["order_date"])
    df["month"] = df["order_date"].dt.to_period("M")

    monthly_sets = df.groupby("month")["customer_id"].apply(set).reset_index()
    monthly_sets.columns = ["month", "customers"]
    monthly_sets = monthly_sets.sort_values("month").reset_index(drop=True)

    rows = []
    for i in range(len(monthly_sets) - 1):
        current_month = monthly_sets.loc[i, "month"]
        current_customers = monthly_sets.loc[i, "customers"]
        next_customers    = monthly_sets.loc[i + 1, "customers"]
        churned_count = len(current_customers - next_customers)
        churn_rate    = churned_count / len(current_customers) * 100
        rows.append({
            "month":         str(current_month),
            "active":        len(current_customers),
            "churned":       churned_count,
            "churn_rate_pct": round(churn_rate, 2),
        })

    trend = pd.DataFrame(rows)
    print("\nMonthly Churn Trend (first 6 months):")
    print(trend.head(6).to_string(index=False))
    return trend


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df = load_features()

    kpis = compute_overall_kpis(df)
    print_kpis(kpis)

    segment_summary = churn_by_segment(df)
    segment_summary.to_csv(
        os.path.join(PROCESSED_DIR, "churn_summary.csv"), index=False
    )
    print(f"\nChurn summary saved to {PROCESSED_DIR}/churn_summary.csv")

    churn_by_category(df)
    identify_high_risk(df)
    churn_indicators(df)

    transactions_csv = os.path.join(
        BASE_DIR, "data", "processed", "transactions_clean.csv"
    )
    monthly_churn_trend(transactions_csv)


if __name__ == "__main__":
    main()
