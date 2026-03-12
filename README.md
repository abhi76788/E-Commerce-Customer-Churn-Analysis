# E-Commerce Customer Churn Analysis

A production-ready Business Analyst project that uses **SQL**, **Python**, and **Tableau** to analyze customer churn in an e-commerce platform. The project covers customer segmentation, RFM analysis, churn prediction, KPI tracking, and actionable retention strategies.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Dataset Description](#dataset-description)
- [Setup & Installation](#setup--installation)
- [SQL Analysis](#sql-analysis)
- [Python Analysis](#python-analysis)
- [Tableau Dashboard](#tableau-dashboard)
- [Key Findings](#key-findings)
- [Business Recommendations](#business-recommendations)

---

## Project Overview

**Objective:** Identify customers at risk of churning, understand behavioral patterns driving churn, and develop data-driven retention strategies.

**Definition of Churn:** A customer is considered *churned* if they have not made a purchase in the **last 90 days** relative to the analysis date.

### Key KPIs Tracked
| KPI | Description |
|-----|-------------|
| **Churn Rate** | % of customers who stopped purchasing in last 90 days |
| **Customer Lifetime Value (CLV)** | Predicted total revenue from a customer |
| **Average Order Value (AOV)** | Mean transaction amount |
| **Repeat Purchase Rate** | % of customers with more than one purchase |
| **Retention Rate** | % of customers retained period-over-period |

---

## Project Structure

```
├── README.md                         # Project documentation
├── data/
│   ├── customers.csv                 # Customer master data (300 customers)
│   └── ecommerce_transactions.csv    # Transaction data (1800+ records, 2022–2023)
├── sql/
│   ├── schema.sql                    # Database schema design
│   ├── customer_segmentation.sql     # RFM analysis & customer tier classification
│   ├── churn_analysis.sql            # Churn rate, retention, cohort analysis
│   └── kpi_queries.sql               # CLV, AOV, repeat purchase rate queries
├── python/
│   ├── requirements.txt              # Python dependencies
│   ├── data_preprocessing.py         # Data cleaning and feature engineering
│   ├── churn_analysis.py             # Churn labeling and behavioral analysis
│   ├── customer_segmentation.py      # RFM scoring + K-means clustering
│   └── visualizations.py             # Charts and dashboards
├── notebooks/
│   └── EDA_Churn_Analysis.ipynb      # Full exploratory data analysis notebook
├── tableau/
│   └── dashboard_guide.md            # Tableau dashboard creation guide
└── reports/
    └── business_insights.md          # Actionable insights and retention strategies
```

---

## Dataset Description

### `data/customers.csv`
| Column | Type | Description |
|--------|------|-------------|
| customer_id | VARCHAR | Unique customer identifier (C0001–C0300) |
| name | VARCHAR | Customer full name |
| email | VARCHAR | Customer email address |
| signup_date | DATE | Date customer registered |
| location | VARCHAR | Customer city |
| segment | VARCHAR | Premium / Regular / Occasional / New |

### `data/ecommerce_transactions.csv`
| Column | Type | Description |
|--------|------|-------------|
| order_id | VARCHAR | Unique order identifier |
| customer_id | VARCHAR | Foreign key to customers |
| order_date | DATE | Date of purchase |
| order_value | DECIMAL | Total order amount (USD) |
| product_category | VARCHAR | Electronics, Clothing, Home & Garden, etc. |
| quantity | INT | Number of items ordered |
| discount_pct | DECIMAL | Discount percentage applied |
| payment_method | VARCHAR | Credit Card, PayPal, etc. |
| return_flag | CHAR | Y = returned, N = not returned |

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or MySQL (for SQL scripts)
- Tableau Desktop or Tableau Public (for dashboard)

### 1. Clone the Repository
```bash
git clone https://github.com/abhi76788/E-Commerce-Customer-Churn-Analysis.git
cd E-Commerce-Customer-Churn-Analysis
```

### 2. Install Python Dependencies
```bash
pip install -r python/requirements.txt
```

### 3. Set Up the Database
```bash
# PostgreSQL example
psql -U postgres -d your_database -f sql/schema.sql
# Then load data using psql \copy or Python SQLAlchemy (see data_preprocessing.py)
```

### 4. Run Python Analysis
```bash
# Step 1: Preprocess data
python python/data_preprocessing.py

# Step 2: Perform churn analysis
python python/churn_analysis.py

# Step 3: Customer segmentation
python python/customer_segmentation.py

# Step 4: Generate visualizations
python python/visualizations.py
```

### 5. Open Jupyter Notebook
```bash
jupyter notebook notebooks/EDA_Churn_Analysis.ipynb
```

---

## SQL Analysis

### Schema (`sql/schema.sql`)
Creates normalized tables: `customers`, `orders`, `products` with proper primary/foreign key constraints and indexes for analytical queries.

### Customer Segmentation (`sql/customer_segmentation.sql`)
- **RFM Scoring**: Recency (days since last purchase), Frequency (number of orders), Monetary (total spend)
- **Customer Tiers**: Champions, Loyal Customers, Potential Loyalists, At Risk, Can't Lose, Lost Customers

### Churn Analysis (`sql/churn_analysis.sql`)
- Monthly churn rate calculation
- Cohort-based retention analysis
- Segment-level churn comparison
- Customer-level churn flag assignment

### KPI Queries (`sql/kpi_queries.sql`)
- Customer Lifetime Value (historical and predictive)
- Average Order Value by segment and period
- Repeat purchase rate
- Monthly active customers trend
- Revenue by product category and customer segment

---

## Python Analysis

Run scripts individually or use the Jupyter notebook for interactive exploration.

| Script | Purpose |
|--------|---------|
| `data_preprocessing.py` | Load CSVs, handle missing values, engineer features |
| `churn_analysis.py` | Label churned customers, analyze behavioral patterns |
| `customer_segmentation.py` | RFM scoring, K-means clustering, segment profiling |
| `visualizations.py` | Generate all charts saved to `reports/figures/` |

---

## Tableau Dashboard

See [`tableau/dashboard_guide.md`](tableau/dashboard_guide.md) for step-by-step instructions to build an interactive dashboard with:
- KPI summary cards
- Churn trend over time
- Customer segment breakdown (RFM)
- Cohort retention heatmap
- Geographic distribution map
- Drill-down filters by time period, segment, and category

---

## Key Findings

1. **Overall Churn Rate**: ~38% of customers churned (no purchase in 90 days)
2. **High-Risk Segments**: "Occasional" and "New" customers churn at 50–60%
3. **Premium customers** have the lowest churn (~10%) but highest CLV impact
4. **Electronics and Clothing** categories show the highest repeat purchase rates
5. **Discount sensitivity**: Customers who received ≥15% discounts had 22% lower churn

---

## Business Recommendations

1. **Personalized Re-engagement Campaigns**: Target "At Risk" and "Can't Lose" segments with personalized discount offers 60 days before expected churn
2. **Loyalty Program**: Introduce a tiered loyalty program to convert "Regular" customers to "Premium"
3. **Onboarding Optimization**: Improve first-30-day experience for "New" customers to reduce early churn
4. **Category-Based Retention**: Use high-engagement categories (Electronics, Clothing) as anchors for cross-selling
5. **Early Warning System**: Flag customers with >45-day purchase gaps for proactive outreach

See [`reports/business_insights.md`](reports/business_insights.md) for the full analysis and implementation roadmap.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)