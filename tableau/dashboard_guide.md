# Tableau Dashboard Guide
## E-Commerce Customer Churn Analysis

This guide walks you through building a professional, interactive Tableau dashboard for the E-Commerce Customer Churn Analysis project.

---

## Prerequisites

- **Tableau Desktop** 2021.4+ or **Tableau Public** (free)
- The processed data files from `data/processed/`:
  - `customer_features.csv`
  - `customer_segments.csv`
  - `transactions_clean.csv`

---

## Step 1: Connect to Data Sources

1. Open Tableau Desktop / Tableau Public
2. Click **"Connect to Data"** → **Text File**
3. Select `data/processed/customer_features.csv`
4. Repeat to add `transactions_clean.csv` as a second data source
5. Create a **Data Relationship**:
   - Join on `customer_id` (left join from transactions to customer_features)

---

## Step 2: Prepare Calculated Fields

Before building sheets, create these calculated fields (right-click in the Data pane → **Create Calculated Field**):

### KPI Calculated Fields

```
// Churn Rate
[Churn Rate] = SUM([Is Churned]) / COUNT([Customer Id])

// Customer Lifetime Value (CLV)
[CLV] = SUM([Monetary])

// Average Order Value (AOV)
[AOV] = AVG([Avg Order Value])

// Repeat Purchase Rate
[Repeat Purchase Rate] = 
  COUNTD(IF [Frequency] > 1 THEN [Customer Id] END) / COUNTD([Customer Id])

// Churn Status Label
[Churn Status] = IF [Is Churned] = 1 THEN "Churned" ELSE "Active" END

// Days Since Last Purchase Bucket
[Recency Bucket] = 
  IF [Recency Days] <= 30 THEN "0-30 days"
  ELSEIF [Recency Days] <= 60 THEN "31-60 days"
  ELSEIF [Recency Days] <= 90 THEN "61-90 days"
  ELSE "90+ days (Churned)"
  END

// At-Risk Flag (60-90 days inactive, not yet churned)
[At Risk] = [Recency Days] >= 60 AND [Recency Days] <= 90 AND [Is Churned] = 0
```

---

## Step 3: Build Individual Sheets

### Sheet 1 – KPI Summary Cards

**Create 4 separate sheets** for each KPI to use as "big number" cards:

**Sheet 1a – Churn Rate Card**
1. Drag `[Churn Rate]` to Text
2. Format as Percentage (1 decimal place)
3. Add a title "Overall Churn Rate"
4. Set background color to a light red/coral

**Sheet 1b – Average CLV Card**
1. Drag `[CLV]` → change to Average → Drag to Text
2. Format as Currency ($)
3. Title: "Avg Customer Lifetime Value"

**Sheet 1c – AOV Card**
1. Drag `[AOV]` to Text, format as Currency
2. Title: "Average Order Value"

**Sheet 1d – Repeat Purchase Rate Card**
1. Drag `[Repeat Purchase Rate]` to Text, format as Percentage
2. Title: "Repeat Purchase Rate"

---

### Sheet 2 – Churn Trend Over Time

1. Drag `Order Date` to **Columns** → truncate to **Month**
2. Drag `[Churn Rate]` calculated field to **Rows**
3. Click **Show Me** → Line Chart
4. Add `Segment` to **Color**
5. Add a **Reference Line** (Analytics pane) showing the overall average
6. Title: "Monthly Churn Rate Trend"
7. Format Y-axis as percentage

---

### Sheet 3 – Customer Segment Breakdown (RFM)

1. Drag `Rfm Segment` to **Rows**
2. Drag `Customer Id` (count distinct) to **Columns**
3. Drag `[Churn Rate]` to **Color** (diverging: green→red)
4. Drag `Monetary` (sum) to **Size**
5. Choose **Bar Chart** from Show Me
6. Sort by count descending
7. Title: "RFM Segment Breakdown"

---

### Sheet 4 – Cohort Retention Heatmap

1. Create a parameter or use the `cohort_month` field in `transactions_clean.csv`
2. Drag `Cohort Month` (from transactions) to **Rows** → format as Month/Year
3. Create a calculated field: `Period Number` = DATEDIFF('month', [Cohort Month], [Order Date])
4. Drag `Period Number` to **Columns**
5. Drag `Customer Id` (count distinct) to **Color/Text** → format as retention %
6. Choose **Text Table** (crosstab)
7. Apply a **Sequential color palette** (white → dark blue)
8. Title: "Cohort Retention Heatmap"

---

### Sheet 5 – Geographic Distribution Map

1. Drag `Location` to the canvas → Tableau auto-geocodes US cities
2. Drag `[Churn Rate]` to **Color**
3. Drag `Customer Id` (count) to **Size**
4. Set color palette to **Red-Green Diverging** (red = high churn)
5. Add a **Label** showing city name
6. Title: "Customer Churn by City"

---

### Sheet 6 – Revenue by Product Category

1. Drag `Product Category` to **Rows**
2. Drag `Order Value` (sum) to **Columns**
3. Drag `Churn Status` to **Color** (green = Active, red = Churned)
4. Choose **Stacked Bar Chart**
5. Sort by total revenue descending
6. Format X-axis as currency
7. Title: "Revenue by Product Category"

---

### Sheet 7 – CLV Distribution

1. Drag `Monetary` to **Columns** → change to **Dimension** (for bin creation)
2. Right-click `Monetary` → **Create Bins** (bin size = 100)
3. Drag `Monetary (bin)` to **Columns**, count of `Customer Id` to **Rows**
4. Drag `Segment` to **Color**
5. Choose **Histogram**
6. Title: "CLV Distribution by Segment"

---

### Sheet 8 – High-Risk Customer Table

1. Drag `Customer Id` to the view → add `Name`, `Segment`, `Recency Days`, `Frequency`, `Monetary`
2. Apply a filter: `Recency Days` BETWEEN 60 AND 90
3. Sort by `Monetary` descending
4. Apply **conditional formatting**: red highlight where `Recency Days` > 75
5. Title: "High-Risk Customer List (Pre-Churn Window)"

---

## Step 4: Build the Dashboard

1. Click **New Dashboard** (bottom tab)
2. Set dashboard size: **Fixed** → 1400 × 900 px (or Automatic)

### Layout

```
┌────────────────────────────────────────────────────────────┐
│  [KPI: Churn Rate] [KPI: CLV] [KPI: AOV] [KPI: RPR]       │  Row 1 (KPI Cards)
├────────────────────────────────────────────────────────────┤
│  Monthly Churn Trend (Sheet 2)     │  RFM Segments (Sh.3)  │  Row 2
├────────────────────────────────────┼───────────────────────┤
│  Cohort Retention Heatmap (Sh.4)   │  Category Revenue(6)  │  Row 3
├────────────────────────────────────┼───────────────────────┤
│  Geographic Map (Sheet 5)          │  CLV Distribution(7)  │  Row 4
└────────────────────────────────────────────────────────────┘
```

3. Drag each sheet to its position in the layout
4. Add a **Text** object at the top: title and date

---

## Step 5: Add Filters and Interactivity

### Global Filters (apply to all sheets)

1. Right-click on the `Churn Trend` sheet → **Filters** → `Order Date`
2. Show filter → set to **Date Range Slider**
3. Right-click → **Apply to Worksheets** → **All Using This Data Source**

### Segment Filter

1. Add `Segment` as a quick filter (checkbox style)
2. Apply to all sheets

### Category Filter

1. Add `Product Category` as a quick filter (dropdown)

### Actions

1. **Dashboard** → **Actions** → **Add Action** → **Filter**
2. Source: **RFM Segments sheet** → Target: **All Sheets**
3. This allows clicking a segment to filter the entire dashboard

---

## Step 6: Formatting Tips

- **Colors**: Use a consistent brand palette
  - Active customers: `#4CAF50` (green)
  - Churned customers: `#F44336` (red)
  - At-risk: `#FF9800` (orange)
  - Primary accent: `#1976D2` (blue)
- **Fonts**: Use a clean sans-serif (Tableau's default or Arial)
- **Background**: Light gray (`#F5F5F5`) for the dashboard background
- **Sheet borders**: Subtle border, 1px `#E0E0E0`
- **Tooltips**: Customize each sheet's tooltip with relevant metrics

---

## Step 7: Publish & Share

### Tableau Public (Free)
1. **File** → **Save to Tableau Public As...**
2. Sign in to your Tableau Public account
3. Set visibility to Public
4. Share the URL

### Tableau Server / Online
1. **Server** → **Publish Workbook**
2. Select project and set permissions
3. Enable **Subscribe** for stakeholders to receive scheduled PDF snapshots

---

## Dashboard Maintenance

| Task | Frequency | How |
|------|-----------|-----|
| Refresh data extract | Weekly | Tableau Data Extract refresh |
| Update analysis date | Monthly | Update `ANALYSIS_DATE` in Python scripts |
| Review KPI targets | Quarterly | Update reference lines |
| Add new segments | As needed | Re-run segmentation scripts |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cities not mapping correctly | Use **Edit Locations** → assign country = USA |
| Date format mismatch | Set `Order Date` field type to Date in Tableau |
| Calculated field error | Ensure `Is Churned` is a Numeric (integer) field |
| Heatmap missing values | Replace NULL with 0 using `ZN()` function |
