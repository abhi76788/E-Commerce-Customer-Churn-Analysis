"""
data_preprocessing.py
=====================
Load, clean, and engineer features from the e-commerce dataset.

Outputs:
    - data/processed/customers_clean.csv
    - data/processed/transactions_clean.csv
    - data/processed/customer_features.csv   (one row per customer)
"""

import os
import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CUSTOMERS_CSV     = os.path.join(DATA_DIR, "customers.csv")
TRANSACTIONS_CSV  = os.path.join(DATA_DIR, "ecommerce_transactions.csv")
ANALYSIS_DATE     = pd.Timestamp("2024-01-01")   # reference date for recency/churn


# ── 1. Load Data ─────────────────────────────────────────────────────────────
def load_data():
    """Load customer and transaction CSV files."""
    customers = pd.read_csv(CUSTOMERS_CSV, parse_dates=["signup_date"])
    transactions = pd.read_csv(
        TRANSACTIONS_CSV,
        parse_dates=["order_date"],
        dtype={
            "order_id": str,
            "customer_id": str,
            "return_flag": str,
        }
    )
    print(f"Loaded {len(customers):,} customers and {len(transactions):,} transactions.")
    return customers, transactions


# ── 2. Clean Customers ───────────────────────────────────────────────────────
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, fill missing, standardise segment labels."""
    original_len = len(df)

    # Drop duplicate customer IDs
    df = df.drop_duplicates(subset="customer_id")

    # Standardise segment capitalisation
    df["segment"] = df["segment"].str.strip().str.title()

    # Fill missing location with 'Unknown'
    df["location"] = df["location"].fillna("Unknown")

    # Clip implausible signup dates
    df = df[df["signup_date"] <= ANALYSIS_DATE]

    print(f"Customers cleaned: {original_len} → {len(df)} rows.")
    return df.reset_index(drop=True)


# ── 3. Clean Transactions ────────────────────────────────────────────────────
def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, fix types, drop invalid rows."""
    original_len = len(df)

    # Drop duplicate order IDs
    df = df.drop_duplicates(subset="order_id")

    # Remove orders with non-positive order values
    df = df[df["order_value"] > 0]

    # Clip discount percentage to [0, 100]
    df["discount_pct"] = df["discount_pct"].clip(lower=0, upper=100).fillna(0)

    # Standardise return_flag
    df["return_flag"] = df["return_flag"].str.strip().str.upper().fillna("N")
    df = df[df["return_flag"].isin(["Y", "N"])]

    # Drop orders outside analysis window
    df = df[(df["order_date"] >= pd.Timestamp("2022-01-01")) &
            (df["order_date"] <= ANALYSIS_DATE)]

    # Standardise product_category
    df["product_category"] = df["product_category"].str.strip().str.title()

    print(f"Transactions cleaned: {original_len} → {len(df)} rows.")
    return df.reset_index(drop=True)


# ── 4. Feature Engineering ───────────────────────────────────────────────────
def build_customer_features(customers: pd.DataFrame,
                             transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Create one row per customer with engineered features for analysis.

    Features:
        - recency_days          : days since last purchase
        - frequency             : number of valid (non-returned) orders
        - monetary              : total spend (non-returned)
        - avg_order_value       : average order size
        - max_order_value       : highest single order
        - num_categories        : distinct product categories purchased
        - preferred_category    : most purchased category
        - discount_order_rate   : fraction of orders with any discount
        - return_rate           : fraction of orders returned
        - customer_age_days     : days since signup
        - avg_days_between_orders : average inter-purchase interval
        - is_churned            : 1 if recency_days > 90, else 0
    """
    # Only non-returned orders for spend metrics
    valid = transactions[transactions["return_flag"] == "N"].copy()

    # ── Recency / Frequency / Monetary ──────────────────────────────────────
    rfm = valid.groupby("customer_id").agg(
        last_purchase_date=("order_date", "max"),
        frequency=("order_id", "count"),
        monetary=("order_value", "sum"),
        avg_order_value=("order_value", "mean"),
        max_order_value=("order_value", "max"),
        num_categories=("product_category", "nunique"),
        preferred_category=("product_category", lambda x: x.value_counts().index[0]),
    ).reset_index()

    rfm["recency_days"] = (ANALYSIS_DATE - rfm["last_purchase_date"]).dt.days

    # ── Discount behaviour ───────────────────────────────────────────────────
    discount_info = transactions.groupby("customer_id").agg(
        total_orders_raw=("order_id", "count"),
        discounted_orders=("discount_pct", lambda x: (x > 0).sum()),
        returned_orders=("return_flag", lambda x: (x == "Y").sum()),
    ).reset_index()

    discount_info["discount_order_rate"] = (
        discount_info["discounted_orders"] / discount_info["total_orders_raw"]
    ).round(4)
    discount_info["return_rate"] = (
        discount_info["returned_orders"] / discount_info["total_orders_raw"]
    ).round(4)

    # ── Average inter-purchase interval ─────────────────────────────────────
    def avg_interval(grp):
        dates = grp.sort_values().reset_index(drop=True)
        if len(dates) < 2:
            return np.nan
        return (dates.diff().dt.days.dropna()).mean()

    intervals = (
        valid.groupby("customer_id")["order_date"]
        .apply(avg_interval)
        .rename("avg_days_between_orders")
        .reset_index()
    )

    # ── Customer age ─────────────────────────────────────────────────────────
    customers_copy = customers.copy()
    customers_copy["customer_age_days"] = (
        ANALYSIS_DATE - customers_copy["signup_date"]
    ).dt.days

    # ── Merge everything ─────────────────────────────────────────────────────
    features = (
        customers_copy
        .merge(rfm, on="customer_id", how="left")
        .merge(discount_info[["customer_id", "total_orders_raw",
                               "discount_order_rate", "return_rate"]],
               on="customer_id", how="left")
        .merge(intervals, on="customer_id", how="left")
    )

    # Fill customers who never ordered
    features["frequency"]    = features["frequency"].fillna(0).astype(int)
    features["monetary"]     = features["monetary"].fillna(0).round(2)
    features["recency_days"] = features["recency_days"].fillna(
        features["customer_age_days"]
    ).astype(int)

    # ── Churn label ──────────────────────────────────────────────────────────
    features["is_churned"] = (features["recency_days"] > 90).astype(int)

    # ── Round floats ─────────────────────────────────────────────────────────
    for col in ["avg_order_value", "max_order_value", "monetary",
                "avg_days_between_orders"]:
        features[col] = features[col].round(2)

    print(f"Customer features built: {len(features):,} rows, "
          f"{len(features.columns)} columns.")
    print(f"Churn rate: {features['is_churned'].mean() * 100:.1f}%")
    return features


# ── 5. Save Processed Files ───────────────────────────────────────────────────
def save_processed(customers_clean, transactions_clean, features):
    customers_clean.to_csv(
        os.path.join(OUTPUT_DIR, "customers_clean.csv"), index=False
    )
    transactions_clean.to_csv(
        os.path.join(OUTPUT_DIR, "transactions_clean.csv"), index=False
    )
    features.to_csv(
        os.path.join(OUTPUT_DIR, "customer_features.csv"), index=False
    )
    print(f"Processed files saved to {OUTPUT_DIR}/")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    customers_raw, transactions_raw = load_data()
    customers_clean = clean_customers(customers_raw)
    transactions_clean = clean_transactions(transactions_raw)
    features = build_customer_features(customers_clean, transactions_clean)
    save_processed(customers_clean, transactions_clean, features)
    return customers_clean, transactions_clean, features


if __name__ == "__main__":
    main()
