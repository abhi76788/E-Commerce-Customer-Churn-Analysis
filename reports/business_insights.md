# Business Insights & Retention Strategies
## E-Commerce Customer Churn Analysis

**Date:** January 2024  
**Prepared by:** Business Analytics Team  
**Data Period:** January 2022 – December 2023

---

## Executive Summary

This report presents the findings from a comprehensive analysis of customer churn behaviour across our e-commerce platform. Using RFM (Recency, Frequency, Monetary) segmentation, cohort analysis, and machine learning clustering, we identified the key drivers of customer attrition and developed actionable retention strategies.

**Key Headline Numbers:**
| Metric | Value |
|--------|-------|
| Total Customers Analysed | 300 |
| Overall Churn Rate | ~38% |
| Average Order Value (Active) | $142 |
| Average CLV (Active) | $687 |
| Repeat Purchase Rate | ~72% |
| Monthly Revenue at Risk | ~$28,000 |

---

## 1. Churn Rate Analysis

### 1.1 Overall Churn Definition
A customer is classified as **churned** if they have not made a purchase within the last **90 days** from the analysis date (January 1, 2024).

### 1.2 Churn Rate by Customer Segment

| Segment | Customers | Churn Rate | Avg CLV | Revenue Risk |
|---------|-----------|------------|---------|--------------|
| New | 78 | 60.3% | $89 | High |
| Occasional | 72 | 50.0% | $118 | High |
| Regular | 85 | 25.0% | $342 | Medium |
| Premium | 65 | 10.0% | $1,240 | Low |

**Insight:** The "New" and "Occasional" segments account for more than half of all churned customers. While their individual CLV is lower, the volume of attrition represents significant lost revenue potential.

### 1.3 Churn Rate by Product Category

| Category | Churn Rate | Avg Orders/Customer | Notes |
|----------|------------|---------------------|-------|
| Books | 44% | 2.1 | Single-use purchase pattern |
| Toys | 42% | 2.4 | Seasonal purchasing |
| Food & Grocery | 38% | 5.2 | Higher repeat rate |
| Electronics | 31% | 3.8 | Higher AOV anchors retention |
| Clothing | 30% | 4.2 | Fashion cycle drives return visits |
| Beauty | 28% | 4.6 | Consumable repurchase driver |

**Insight:** Categories with consumable or frequently replenished products (Beauty, Food, Clothing) show lower churn. Books and Toys attract one-time buyers.

---

## 2. Customer Segmentation Findings (RFM Analysis)

### 2.1 RFM Segment Distribution

| RFM Segment | % of Customers | Avg CLV | Avg Recency | Priority |
|-------------|----------------|---------|-------------|----------|
| Champions | 8% | $2,100 | 12 days | Retain & Reward |
| Loyal Customers | 14% | $1,450 | 28 days | Upsell |
| Potential Loyalists | 18% | $680 | 45 days | Nurture |
| At Risk | 12% | $890 | 115 days | Re-engage urgently |
| Can't Lose Them | 6% | $1,680 | 145 days | Win-back campaign |
| Hibernating | 16% | $210 | 210 days | Low-cost reactivation |
| Lost | 10% | $95 | 300+ days | Write-off or last-chance offer |
| Others | 16% | $320 | — | Monitor |

### 2.2 Champions Profile
- Average spend: $2,100 over the analysis period
- Purchase 15+ times, mostly in Electronics and Clothing
- 90% live in major metropolitan areas
- Very low sensitivity to discount (buy regardless)
- **Risk:** Competitor poaching or service failures

### 2.3 At-Risk Segment Alert
- 36 customers (12%) classified as "At Risk"
- Were previously high spenders (avg CLV $890)
- Last purchase was 90–150 days ago
- **Immediate action required**

---

## 3. Behavioural Patterns & Churn Indicators

### 3.1 Top Churn Predictors (by correlation strength)

| Feature | Correlation with Churn | Direction |
|---------|----------------------|-----------|
| Recency Days | 0.78 | Positive (more days = more churn) |
| Frequency | -0.65 | Negative (more orders = less churn) |
| Monetary Value | -0.52 | Negative (higher spend = less churn) |
| Avg Days Between Orders | 0.41 | Positive |
| Return Rate | 0.38 | Positive (returns → dissatisfaction) |
| Discount Order Rate | -0.22 | Negative (discounts aid retention) |

### 3.2 Key Behavioural Findings

1. **The 60-Day Cliff**: Customers who go 60+ days without purchasing have a 73% probability of churning by day 90. This creates a critical intervention window.

2. **First 30 Days are Critical**: 35% of "New" segment customers churn after their first purchase without returning. Improving the first-month experience could reduce overall churn by ~8 percentage points.

3. **High Return Rate = High Churn Risk**: Customers with a return rate above 30% are 2.5× more likely to churn. Product quality or expectation management issues should be investigated.

4. **Category Cross-Purchase Reduces Churn**: Customers who purchased across 3+ categories had a churn rate of only 18%, compared to 52% for single-category buyers.

5. **Discount Effectiveness**: Targeted discounts of 10-20% reduced 90-day churn probability by ~22% when applied in the 60-75 day inactivity window.

---

## 4. Cohort Retention Analysis

### 4.1 Monthly Cohort Retention (Summary)

| Cohort | Month 0 | Month 1 | Month 3 | Month 6 | Month 12 |
|--------|---------|---------|---------|---------|----------|
| Jan 2022 | 100% | 42% | 31% | 22% | 15% |
| Apr 2022 | 100% | 38% | 27% | 19% | 12% |
| Jul 2022 | 100% | 45% | 35% | 26% | 18% |
| Oct 2022 | 100% | 41% | 30% | — | — |
| Jan 2023 | 100% | 47% | 33% | — | — |

**Key Finding:** The steepest drop in retention occurs between Month 0 and Month 1 (averaging -58% retention). This represents the biggest leverage point for churn reduction.

### 4.2 Seasonal Patterns
- Q4 (October–December) cohorts show 15–20% better 3-month retention due to holiday purchase momentum
- Summer cohorts (June–August) underperform, suggesting seasonal deal incentives

---

## 5. Actionable Retention Strategies

### Strategy 1: Early Intervention Program (Impact: High, Effort: Medium)
**Target:** Customers at 45-day inactivity mark (pre-churn window)

**Actions:**
- Automated email campaign triggered at day 45 of inactivity
- Personalised product recommendations based on purchase history
- Offer a 10% discount on top-selling items in their preferred category
- Subject line testing: "We miss you" vs. category-specific subject lines

**Expected Impact:** 15-20% reduction in churn for targeted segment
**KPI:** 30-day reactivation rate post-campaign

---

### Strategy 2: New Customer Onboarding Enhancement (Impact: High, Effort: High)
**Target:** All new customers within first 30 days

**Actions:**
- Welcome email series (Day 1, 7, 14, 30) with personalised content
- "Second Purchase Incentive": 15% off second order if placed within 30 days
- Onboarding guide showcasing top products in their first-purchased category
- Loyalty points introduction email at Day 7

**Expected Impact:** Increase Month-1 retention from 42% to 55-60%
**Investment Required:** Email platform automation, customer success team support

---

### Strategy 3: Tiered Loyalty Programme (Impact: High, Effort: High)
**Target:** All active customers

**Tiers:**
| Tier | Annual Spend | Benefits |
|------|-------------|----------|
| Bronze | $0–$299 | 5% cashback, free shipping on orders $75+ |
| Silver | $300–$799 | 8% cashback, free shipping on $50+, early access to sales |
| Gold | $800–$1,499 | 12% cashback, free shipping always, dedicated support |
| Platinum | $1,500+ | 15% cashback, VIP events, personal shopper |

**Expected Impact:** Increase average frequency by 20%, reduce Premium segment churn to <5%

---

### Strategy 4: Category Cross-Sell Programme (Impact: Medium, Effort: Low)
**Target:** Single-category buyers (high churn risk)

**Actions:**
- Post-purchase recommendation emails featuring complementary categories
- "Bundle deals" combining purchased category with adjacent categories
- Targeted homepage personalisation for returning single-category visitors

**Expected Impact:** Increase multi-category purchase rate from 35% to 50%
**Estimated Revenue Lift:** $45,000 annually

---

### Strategy 5: Win-Back Campaign for "Can't Lose Them" Segment (Impact: High, Effort: Low)
**Target:** 18 customers in "Can't Lose Them" RFM segment

**Actions:**
- Personal outreach from customer success manager (high-CLV accounts)
- Premium incentive: 20% discount + free expedited shipping
- Survey to understand reason for churn (product, price, competitor)
- Phone call for top 5 accounts by historical CLV

**Expected Impact:** Reactivate 40-50% of segment ($28,000–$35,000 revenue recovery)
**Urgency:** Immediate (within 2 weeks)

---

### Strategy 6: Return Experience Improvement (Impact: Medium, Effort: Medium)
**Target:** Customers with return rate >30%

**Actions:**
- Improved product photography and detailed specifications
- "Ask a question" feature on product pages
- Size guides and comparison tools for Clothing
- Post-return survey to categorise return reasons

**Expected Impact:** Reduce return-related churn by 15%

---

## 6. Revenue Impact Summary

| Strategy | Investment | Revenue Retained | ROI |
|----------|-----------|-----------------|-----|
| Early Intervention Program | $8,000/year | $52,000 | 550% |
| New Customer Onboarding | $25,000 (one-time) | $95,000/year | 280% |
| Loyalty Programme | $40,000 (one-time) | $180,000/year | 350% |
| Category Cross-Sell | $5,000/year | $45,000/year | 800% |
| Win-Back Campaign | $3,000 (immediate) | $28,000–$35,000 | 1000%+ |
| Return Experience | $15,000 (one-time) | $30,000/year | 100% |

---

## 7. Implementation Roadmap

### Phase 1 – Immediate (0–30 Days)
- [ ] Launch Win-Back Campaign for "Can't Lose Them" segment (18 customers)
- [ ] Set up automated 45-day inactivity email trigger
- [ ] Establish KPI tracking dashboard in Tableau

### Phase 2 – Short-Term (1–3 Months)
- [ ] Design and launch New Customer Onboarding email series
- [ ] Implement Cross-Sell recommendation engine
- [ ] Pilot loyalty programme with Premium and Regular segments

### Phase 3 – Medium-Term (3–6 Months)
- [ ] Full loyalty programme rollout
- [ ] Product page improvements to reduce return rates
- [ ] A/B test re-engagement campaign variations

### Phase 4 – Long-Term (6–12 Months)
- [ ] Predictive churn model deployment for real-time risk scoring
- [ ] Personalisation engine integration across all channels
- [ ] Quarterly business review using updated cohort analysis

---

## 8. Monitoring & Success Metrics

Track these KPIs monthly to measure strategy effectiveness:

| KPI | Current | 3-Month Target | 12-Month Target |
|-----|---------|----------------|-----------------|
| Overall Churn Rate | 38% | 32% | 25% |
| Month-1 Retention | 42% | 50% | 58% |
| Repeat Purchase Rate | 72% | 78% | 85% |
| Average CLV | $687 | $750 | $900 |
| Multi-Category Purchase Rate | 35% | 42% | 55% |
| Customer Satisfaction (CSAT) | — | 4.0/5 | 4.3/5 |

---

## 9. Data Quality Notes & Limitations

1. **Analysis Period**: 2 years of data (2022–2023); longer history would improve cohort accuracy
2. **Churn Threshold**: 90-day definition is industry-standard but may need calibration for seasonal categories
3. **No customer feedback data**: Incorporating NPS/CSAT scores would strengthen churn prediction
4. **CLV Calculation**: Historical CLV used; predictive CLV requires longer customer tenure data
5. **External Factors**: Competitor promotions and macro-economic factors not captured

---

## 10. Next Steps

1. **Data Collection Enhancement**: Begin capturing NPS scores and return reasons
2. **Machine Learning Model**: Build a supervised churn prediction model using the features identified in this analysis
3. **Real-Time Dashboard**: Connect Tableau dashboard to live database for daily KPI monitoring
4. **Customer Survey**: Launch a targeted survey for churned customers to identify qualitative reasons
5. **A/B Testing Framework**: Set up systematic testing of retention interventions

---

*Report prepared using data from `data/processed/customer_features.csv` and `data/processed/transactions_clean.csv`.*  
*For questions, contact the Business Analytics Team.*
