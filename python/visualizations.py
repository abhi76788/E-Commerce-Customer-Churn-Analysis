"""
visualizations.py
=================
Generate all charts for the E-Commerce Churn Analysis project.

Reads:
    data/processed/customer_features.csv
    data/processed/customer_segments.csv
    data/processed/transactions_clean.csv

Outputs (PNG files saved to reports/figures/):
    01_churn_rate_by_segment.png
    02_monthly_churn_trend.png
    03_rfm_segment_distribution.png
    04_clv_distribution.png
    05_cohort_retention_heatmap.png
    06_purchase_frequency_distribution.png
    07_aov_by_segment.png
    08_category_revenue.png
    09_churn_indicators.png
    10_geographic_distribution.png
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")            # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FIGURES_DIR   = os.path.join(BASE_DIR, "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
PALETTE = sns.color_palette("muted")
CHURN_PALETTE = {"Active": "#4CAF50", "Churned": "#F44336"}


def _save(fig, name: str) -> None:
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── 1. Churn Rate by Segment ──────────────────────────────────────────────────
def plot_churn_by_segment(df: pd.DataFrame) -> None:
    grp = df.groupby("segment")["is_churned"].mean().mul(100).reset_index()
    grp.columns = ["segment", "churn_rate_pct"]
    grp = grp.sort_values("churn_rate_pct", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(grp["segment"], grp["churn_rate_pct"],
                   color=sns.color_palette("Reds_r", len(grp)))
    ax.set_xlabel("Churn Rate (%)")
    ax.set_title("Churn Rate by Customer Segment", fontsize=14, fontweight="bold")
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.set_xlim(0, grp["churn_rate_pct"].max() * 1.2)
    fig.tight_layout()
    _save(fig, "01_churn_rate_by_segment.png")


# ── 2. Monthly Churn Trend ────────────────────────────────────────────────────
def plot_monthly_churn_trend(transactions: pd.DataFrame) -> None:
    df = transactions.copy()
    df["month"] = df["order_date"].dt.to_period("M")
    monthly_sets = df.groupby("month")["customer_id"].apply(set).reset_index()
    monthly_sets.columns = ["month", "customers"]
    monthly_sets = monthly_sets.sort_values("month").reset_index(drop=True)

    rows = []
    for i in range(len(monthly_sets) - 1):
        cur  = monthly_sets.loc[i, "customers"]
        nxt  = monthly_sets.loc[i + 1, "customers"]
        rows.append({
            "month":          str(monthly_sets.loc[i, "month"]),
            "active":         len(cur),
            "churn_rate_pct": len(cur - nxt) / len(cur) * 100,
        })
    trend = pd.DataFrame(rows)

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()
    ax1.bar(trend["month"], trend["active"], color="#90CAF9", alpha=0.7, label="Active Customers")
    ax2.plot(trend["month"], trend["churn_rate_pct"], color="#E53935",
             marker="o", linewidth=2, label="Churn Rate %")

    ax1.set_xlabel("Month")
    ax1.set_ylabel("Active Customers", color="#1565C0")
    ax2.set_ylabel("Monthly Churn Rate (%)", color="#E53935")
    ax1.set_title("Monthly Active Customers & Churn Rate Trend", fontsize=14, fontweight="bold")

    step = max(1, len(trend) // 12)
    ax1.set_xticks(range(0, len(trend), step))
    ax1.set_xticklabels([trend["month"].iloc[i] for i in range(0, len(trend), step)],
                         rotation=45, ha="right")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    fig.tight_layout()
    _save(fig, "02_monthly_churn_trend.png")


# ── 3. RFM Segment Distribution ───────────────────────────────────────────────
def plot_rfm_segment_distribution(df: pd.DataFrame) -> None:
    if "rfm_segment" not in df.columns:
        print("  rfm_segment column not found; skipping.")
        return

    counts = df["rfm_segment"].value_counts()
    colors = sns.color_palette("Set2", len(counts))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        counts, labels=counts.index, colors=colors,
        autopct="%1.1f%%", startangle=140,
        textprops={"fontsize": 9}
    )
    ax.set_title("Customer Distribution by RFM Segment",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    _save(fig, "03_rfm_segment_distribution.png")


# ── 4. CLV Distribution ───────────────────────────────────────────────────────
def plot_clv_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Overall CLV histogram
    axes[0].hist(df["monetary"].clip(upper=df["monetary"].quantile(0.99)),
                 bins=40, color="#42A5F5", edgecolor="white")
    axes[0].set_xlabel("Total Spend (USD)")
    axes[0].set_ylabel("Number of Customers")
    axes[0].set_title("CLV Distribution (Capped at 99th pct)", fontsize=12, fontweight="bold")

    # CLV by segment – box plot
    seg_order = df.groupby("segment")["monetary"].median().sort_values(ascending=False).index.tolist()
    seg_data = [df[df["segment"] == s]["monetary"].dropna().values for s in seg_order]
    axes[1].boxplot(seg_data, labels=seg_order, patch_artist=True,
                    boxprops=dict(facecolor="#90CAF9"))
    axes[1].set_title("CLV Distribution by Segment", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Segment")
    axes[1].set_ylabel("Total Spend (USD)")
    plt.suptitle("")

    fig.tight_layout()
    _save(fig, "04_clv_distribution.png")


# ── 5. Cohort Retention Heatmap ───────────────────────────────────────────────
def plot_cohort_retention(transactions: pd.DataFrame) -> None:
    df = transactions.copy()
    df["cohort_month"]  = df.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")
    df["order_period"]  = df["order_date"].dt.to_period("M")
    df["period_number"] = (df["order_period"] - df["cohort_month"]).apply(lambda x: x.n)

    cohort_data = (
        df.groupby(["cohort_month", "period_number"])["customer_id"]
        .nunique()
        .reset_index()
    )
    cohort_data.columns = ["cohort_month", "period_number", "customers"]

    cohort_pivot = cohort_data.pivot(index="cohort_month",
                                     columns="period_number",
                                     values="customers")
    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_sizes, axis=0).round(4) * 100

    # Limit to first 12 periods for readability
    retention = retention.iloc[:, :13]

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        retention.astype(float),
        annot=True, fmt=".0f", linewidths=0.5,
        cmap="YlGnBu", ax=ax,
        annot_kws={"size": 8},
        cbar_kws={"label": "Retention Rate (%)"}
    )
    ax.set_title("Cohort Retention Heatmap (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Months Since First Purchase")
    ax.set_ylabel("Cohort (First Purchase Month)")
    ax.set_yticklabels([str(m) for m in retention.index], rotation=0)
    fig.tight_layout()
    _save(fig, "05_cohort_retention_heatmap.png")


# ── 6. Purchase Frequency Distribution ───────────────────────────────────────
def plot_purchase_frequency(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    freq_capped = df["frequency"].clip(upper=df["frequency"].quantile(0.95))
    ax.hist(freq_capped, bins=30, color="#66BB6A", edgecolor="white")
    ax.set_xlabel("Number of Orders per Customer")
    ax.set_ylabel("Number of Customers")
    ax.set_title("Purchase Frequency Distribution",
                 fontsize=14, fontweight="bold")
    ax.axvline(df["frequency"].mean(), color="red", linestyle="--",
               label=f"Mean = {df['frequency'].mean():.1f}")
    ax.axvline(df["frequency"].median(), color="orange", linestyle="--",
               label=f"Median = {df['frequency'].median():.0f}")
    ax.legend()
    fig.tight_layout()
    _save(fig, "06_purchase_frequency_distribution.png")


# ── 7. AOV by Segment ────────────────────────────────────────────────────────
def plot_aov_by_segment(df: pd.DataFrame) -> None:
    grp = df.groupby("segment")["avg_order_value"].mean().reset_index()
    grp = grp.sort_values("avg_order_value", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(grp["segment"], grp["avg_order_value"],
                  color=sns.color_palette("Blues_r", len(grp)))
    ax.set_ylabel("Average Order Value (USD)")
    ax.set_title("Average Order Value by Customer Segment",
                 fontsize=14, fontweight="bold")
    ax.bar_label(bars, fmt="$%.0f", padding=4)
    fig.tight_layout()
    _save(fig, "07_aov_by_segment.png")


# ── 8. Revenue by Product Category ───────────────────────────────────────────
def plot_category_revenue(transactions: pd.DataFrame) -> None:
    valid = transactions[transactions["return_flag"] == "N"]
    grp = valid.groupby("product_category")["order_value"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(grp.index, grp.values,
                   color=sns.color_palette("viridis", len(grp)))
    ax.set_xlabel("Total Revenue (USD)")
    ax.set_title("Total Revenue by Product Category",
                 fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"${x:,.0f}"
    ))
    ax.bar_label(bars, fmt="$%.0f", padding=4, fontsize=8)
    fig.tight_layout()
    _save(fig, "08_category_revenue.png")


# ── 9. Churn Indicators (Correlation) ────────────────────────────────────────
def plot_churn_indicators(df: pd.DataFrame) -> None:
    numeric_cols = [
        "recency_days", "frequency", "monetary", "avg_order_value",
        "num_categories", "discount_order_rate", "return_rate",
        "customer_age_days", "avg_days_between_orders",
    ]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available + ["is_churned"]].corr()["is_churned"].drop("is_churned")
    corr_abs = corr.abs().sort_values()

    colors = ["#EF5350" if corr[c] > 0 else "#42A5F5" for c in corr_abs.index]
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(corr_abs.index, corr_abs.values, color=colors)
    ax.set_xlabel("Absolute Correlation with Churn")
    ax.set_title("Churn Indicators (Feature-Churn Correlation)",
                 fontsize=14, fontweight="bold")
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=9)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#EF5350", label="Positive correlation"),
        Patch(facecolor="#42A5F5", label="Negative correlation"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")
    fig.tight_layout()
    _save(fig, "09_churn_indicators.png")


# ── 10. Geographic Distribution ──────────────────────────────────────────────
def plot_geographic_distribution(df: pd.DataFrame) -> None:
    grp = df.groupby("location").agg(
        customers=("customer_id", "count"),
        churn_rate=("is_churned", "mean"),
        avg_monetary=("monetary", "mean"),
    ).reset_index()
    grp["churn_rate_pct"] = (grp["churn_rate"] * 100).round(1)
    grp = grp.sort_values("customers", ascending=False).head(15)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Customer count
    axes[0].barh(grp["location"], grp["customers"],
                  color="#42A5F5")
    axes[0].set_title("Customers by City (Top 15)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Number of Customers")
    axes[0].invert_yaxis()

    # Churn rate
    clrs = ["#EF5350" if r > grp["churn_rate_pct"].mean() else "#66BB6A"
            for r in grp["churn_rate_pct"]]
    axes[1].barh(grp["location"], grp["churn_rate_pct"], color=clrs)
    axes[1].set_title("Churn Rate by City (%)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Churn Rate (%)")
    axes[1].invert_yaxis()
    axes[1].axvline(grp["churn_rate_pct"].mean(), color="black",
                     linestyle="--", label="Avg")
    axes[1].legend()

    fig.tight_layout()
    _save(fig, "10_geographic_distribution.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating visualizations …")

    # Load data
    features_csv     = os.path.join(PROCESSED_DIR, "customer_features.csv")
    segments_csv     = os.path.join(PROCESSED_DIR, "customer_segments.csv")
    transactions_csv = os.path.join(PROCESSED_DIR, "transactions_clean.csv")

    if not os.path.exists(features_csv):
        raise FileNotFoundError(
            "Run data_preprocessing.py and customer_segmentation.py first."
        )

    features     = pd.read_csv(features_csv)
    transactions = pd.read_csv(transactions_csv, parse_dates=["order_date"])

    if os.path.exists(segments_csv):
        segments = pd.read_csv(segments_csv)
    else:
        segments = features.copy()

    plot_churn_by_segment(features)
    plot_monthly_churn_trend(transactions)
    plot_rfm_segment_distribution(segments)
    plot_clv_distribution(features)
    plot_cohort_retention(transactions)
    plot_purchase_frequency(features)
    plot_aov_by_segment(features)
    plot_category_revenue(transactions)
    plot_churn_indicators(features)
    plot_geographic_distribution(features)

    print(f"\nAll charts saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
