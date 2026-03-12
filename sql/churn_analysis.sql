-- ============================================================
-- E-Commerce Customer Churn Analysis – Churn Analysis Queries
-- Churn Definition: no purchase in the last 90 days
-- ============================================================

-- ============================================================
-- 1. CUSTOMER-LEVEL CHURN FLAG
--    Label each customer as churned (1) or active (0)
-- ============================================================
SELECT
    c.customer_id,
    c.name,
    c.segment,
    c.location,
    MAX(o.order_date)                              AS last_purchase_date,
    CURRENT_DATE - MAX(o.order_date)               AS days_inactive,
    COUNT(DISTINCT o.order_id)                     AS total_orders,
    ROUND(SUM(o.order_value), 2)                   AS total_spend,
    CASE
        WHEN CURRENT_DATE - MAX(o.order_date) > 90 THEN 1
        ELSE 0
    END                                            AS is_churned
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.segment, c.location
ORDER BY days_inactive DESC;


-- ============================================================
-- 2. OVERALL CHURN RATE
-- ============================================================
WITH customer_status AS (
    SELECT
        c.customer_id,
        CASE
            WHEN CURRENT_DATE - MAX(o.order_date) > 90 THEN 'Churned'
            ELSE 'Active'
        END AS status
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
)
SELECT
    COUNT(*)                                                    AS total_customers,
    SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)        AS churned_customers,
    SUM(CASE WHEN status = 'Active'  THEN 1 ELSE 0 END)        AS active_customers,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                           AS churn_rate_pct
FROM customer_status;


-- ============================================================
-- 3. CHURN RATE BY CUSTOMER SEGMENT
-- ============================================================
WITH customer_status AS (
    SELECT
        c.customer_id,
        c.segment,
        CASE
            WHEN CURRENT_DATE - MAX(o.order_date) > 90 THEN 'Churned'
            ELSE 'Active'
        END AS status
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.segment
)
SELECT
    segment,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)            AS churned,
    SUM(CASE WHEN status = 'Active'  THEN 1 ELSE 0 END)            AS active,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                               AS churn_rate_pct
FROM customer_status
GROUP BY segment
ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 4. MONTHLY CHURN RATE TREND
--    Customers who had a purchase in month M but not in M+1
-- ============================================================
WITH monthly_activity AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date)  AS activity_month
    FROM orders
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
monthly_pairs AS (
    SELECT
        a.activity_month,
        a.customer_id,
        CASE
            WHEN b.customer_id IS NULL THEN 1
            ELSE 0
        END AS churned_next_month
    FROM monthly_activity a
    LEFT JOIN monthly_activity b
        ON  a.customer_id    = b.customer_id
        AND b.activity_month = a.activity_month + INTERVAL '1 month'
)
SELECT
    activity_month,
    COUNT(DISTINCT customer_id)                                  AS active_customers,
    SUM(churned_next_month)                                      AS churned_next_month,
    ROUND(
        100.0 * SUM(churned_next_month) / COUNT(DISTINCT customer_id), 2
    )                                                            AS monthly_churn_rate_pct
FROM monthly_pairs
GROUP BY activity_month
ORDER BY activity_month;


-- ============================================================
-- 5. COHORT RETENTION ANALYSIS
--    Track what % of each monthly cohort is still active
--    in subsequent months
-- ============================================================
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date))  AS cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_activity AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_date)     AS order_month,
        -- Number of months since first purchase
        EXTRACT(
            EPOCH FROM DATE_TRUNC('month', o.order_date) - c.cohort_month
        ) / 2592000                           AS months_since_first_purchase
    FROM cohorts c
    INNER JOIN orders o ON c.customer_id = o.customer_id
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    cs.cohort_size,
    CAST(ca.months_since_first_purchase AS INT)  AS month_number,
    COUNT(DISTINCT ca.customer_id)               AS retained_customers,
    ROUND(
        100.0 * COUNT(DISTINCT ca.customer_id) / cs.cohort_size, 2
    )                                            AS retention_rate_pct
FROM cohort_activity ca
INNER JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
GROUP BY ca.cohort_month, cs.cohort_size, ca.months_since_first_purchase
ORDER BY ca.cohort_month, month_number;


-- ============================================================
-- 6. RETENTION RATE PERIOD-OVER-PERIOD (Monthly)
-- ============================================================
WITH monthly_customers AS (
    SELECT
        DATE_TRUNC('month', order_date)  AS month,
        COUNT(DISTINCT customer_id)      AS active_customers
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
),
retained AS (
    SELECT
        a.month                          AS current_month,
        b.month                          AS prior_month,
        COUNT(DISTINCT a.customer_id)    AS retained_count
    FROM (
        SELECT DISTINCT DATE_TRUNC('month', order_date) AS month, customer_id FROM orders
    ) a
    INNER JOIN (
        SELECT DISTINCT DATE_TRUNC('month', order_date) AS month, customer_id FROM orders
    ) b
        ON  a.customer_id = b.customer_id
        AND a.month = b.month + INTERVAL '1 month'
    GROUP BY a.month, b.month
)
SELECT
    mc.month,
    mc.active_customers,
    COALESCE(r.retained_count, 0)                       AS retained_from_prior_month,
    ROUND(
        100.0 * COALESCE(r.retained_count, 0) / mc.active_customers, 2
    )                                                   AS retention_rate_pct
FROM monthly_customers mc
LEFT JOIN retained r ON mc.month = r.current_month
ORDER BY mc.month;


-- ============================================================
-- 7. HIGH-RISK CUSTOMERS (approaching churn threshold)
--    Days inactive between 60–90 days (pre-churn window)
-- ============================================================
SELECT
    c.customer_id,
    c.name,
    c.email,
    c.segment,
    MAX(o.order_date)                          AS last_purchase_date,
    CURRENT_DATE - MAX(o.order_date)           AS days_inactive,
    COUNT(DISTINCT o.order_id)                 AS total_orders,
    ROUND(SUM(o.order_value), 2)               AS total_spend,
    ROUND(AVG(o.order_value), 2)               AS avg_order_value
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.segment
HAVING CURRENT_DATE - MAX(o.order_date) BETWEEN 60 AND 90
ORDER BY days_inactive DESC;
