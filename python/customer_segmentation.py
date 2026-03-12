"""
customer_segmentation.py
========================
RFM-based customer segmentation and K-means clustering.

Reads:
    data/processed/customer_features.csv

Outputs:
    data/processed/customer_segments.csv   (features + RFM + cluster labels)
"""

import os
import warnings
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FEATURES_CSV  = os.path.join(PROCESSED_DIR, "customer_features.csv")


# ── 1. Load Features ─────────────────────────────────────────────────────────
def load_features() -> pd.DataFrame:
    if not os.path.exists(FEATURES_CSV):
        raise FileNotFoundError(
            f"{FEATURES_CSV} not found. Run data_preprocessing.py first."
        )
    df = pd.read_csv(FEATURES_CSV, parse_dates=["signup_date", "last_purchase_date"])
    # Keep only customers who have made at least one purchase
    df = df[df["frequency"] > 0].reset_index(drop=True)
    print(f"Loaded {len(df):,} customers with purchase history.")
    return df


# ── 2. RFM Scoring (1–5 quintiles) ───────────────────────────────────────────
def compute_rfm_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign 1–5 scores to Recency, Frequency, Monetary using quintile ranking.
    Recency: lower = better → descending rank gets higher score.
    """
    df = df.copy()

    # Recency score: shorter recency → higher score
    df["r_score"] = pd.qcut(df["recency_days"].rank(method="first"),
                             q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency score
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"),
                             q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Monetary score
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"),
                             q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]
    df["rfm_cell"]  = (df["r_score"].astype(str)
                       + df["f_score"].astype(str)
                       + df["m_score"].astype(str))
    return df


# ── 3. Map RFM scores to named segments ──────────────────────────────────────
def assign_rfm_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Map RFM score combinations to human-readable customer tiers."""
    def classify(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r == 5 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 4 and f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 3 and f >= 2 and m >= 2:
            return "Potential Loyalists"
        elif r >= 4 and f <= 2:
            return "Recent Customers"
        elif r == 3 and f <= 2:
            return "Promising"
        elif r == 2 and f >= 3 and m >= 3:
            return "Needs Attention"
        elif r == 2 and f <= 2:
            return "About to Sleep"
        elif r <= 2 and f >= 4 and m >= 4:
            return "At Risk"
        elif r == 1 and f >= 3 and m >= 4:
            return "Can't Lose Them"
        elif r <= 2 and f <= 2 and m <= 2:
            return "Hibernating"
        else:
            return "Lost"

    df["rfm_segment"] = df.apply(classify, axis=1)
    return df


# ── 4. RFM Segment Summary ───────────────────────────────────────────────────
def rfm_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("rfm_segment").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
        churn_rate=("is_churned", "mean"),
    ).reset_index()

    summary["churn_rate_pct"] = (summary["churn_rate"] * 100).round(2)
    for col in ["avg_recency", "avg_frequency", "avg_monetary", "total_revenue"]:
        summary[col] = summary[col].round(2)

    summary = summary.sort_values("total_revenue", ascending=False).reset_index(drop=True)
    print("\nRFM Segment Summary:")
    print(summary[["rfm_segment", "customers", "avg_recency", "avg_frequency",
                    "avg_monetary", "churn_rate_pct"]].to_string(index=False))
    return summary


# ── 5. K-Means Clustering ─────────────────────────────────────────────────────
CLUSTER_FEATURES = ["recency_days", "frequency", "monetary",
                     "avg_order_value", "num_categories"]


def find_optimal_k(df: pd.DataFrame,
                   k_range: range = range(2, 9)) -> int:
    """
    Use silhouette score to find the optimal number of clusters.
    Returns the k with the highest silhouette score.
    """
    X = df[CLUSTER_FEATURES].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best_k, best_score = 4, -1
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_score, best_k = score, k

    print(f"Optimal K = {best_k}  (silhouette = {best_score:.4f})")
    return best_k


def kmeans_cluster(df: pd.DataFrame, n_clusters: int = None) -> pd.DataFrame:
    """
    Fit K-means on RFM + order features and assign cluster labels.
    If n_clusters is None, it is determined via silhouette analysis.
    """
    df = df.copy()
    X = df[CLUSTER_FEATURES].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if n_clusters is None:
        n_clusters = find_optimal_k(df)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(X_scaled)

    # Order clusters by mean monetary value so cluster 0 = lowest value
    cluster_order = (
        df.groupby("cluster")["monetary"].mean()
        .sort_values()
        .reset_index()
        .reset_index()
    )
    cluster_order.columns = ["new_cluster", "cluster", "mean_monetary"]
    mapping = dict(zip(cluster_order["cluster"], cluster_order["new_cluster"]))
    df["cluster"] = df["cluster"].map(mapping)

    # Attach descriptive labels
    cluster_labels = {
        0: "Low Value",
        1: "Mid Value",
        2: "High Value",
        3: "Premium",
        4: "VIP",
    }
    df["cluster_label"] = df["cluster"].map(
        lambda c: cluster_labels.get(c, f"Cluster {c}")
    )

    # Print cluster profiles
    profile = df.groupby("cluster_label")[
        ["recency_days", "frequency", "monetary", "avg_order_value", "is_churned"]
    ].mean().round(2)
    profile["size"] = df.groupby("cluster_label")["customer_id"].count()
    print(f"\nK-Means Cluster Profiles (k={n_clusters}):")
    print(profile.to_string())
    return df


# ── 6. Segment Profiling ──────────────────────────────────────────────────────
def profile_segments(df: pd.DataFrame) -> None:
    """Print key stats for each RFM segment."""
    cols = ["rfm_segment", "recency_days", "frequency", "monetary",
            "avg_order_value", "is_churned", "customer_id"]
    available = [c for c in cols if c in df.columns]

    profile = df[available].groupby("rfm_segment").agg(
        count=("customer_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_freq=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        churn_rate=("is_churned", "mean"),
    ).round(2)

    print("\nDetailed Segment Profiles:")
    print(profile.to_string())


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    df = load_features()
    df = compute_rfm_scores(df)
    df = assign_rfm_segment(df)

    rfm_segment_summary(df)
    profile_segments(df)

    df = kmeans_cluster(df, n_clusters=4)

    output_path = os.path.join(PROCESSED_DIR, "customer_segments.csv")
    df.to_csv(output_path, index=False)
    print(f"\nCustomer segments saved to {output_path}")


if __name__ == "__main__":
    main()
