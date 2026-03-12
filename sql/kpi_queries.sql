-- ============================================================
-- E-Commerce Customer Churn Analysis – KPI Queries
-- ============================================================

-- ============================================================
-- 1. AVERAGE ORDER VALUE (AOV)
--    Overall and by segment
-- ============================================================

-- Overall AOV
SELECT
    COUNT(order_id)                     AS total_orders,
    ROUND(SUM(order_value), 2)          AS total_revenue,
    ROUND(AVG(order_value), 2)          AS average_order_value
FROM orders
WHERE return_flag = 'N';

-- AOV by customer segment
SELECT
    c.segment,
    COUNT(o.order_id)                   AS total_orders,
    ROUND(SUM(o.order_value), 2)        AS total_revenue,
    ROUND(AVG(o.order_value), 2)        AS average_order_value,
    ROUND(MIN(o.order_value), 2)        AS min_order_value,
    ROUND(MAX(o.order_value), 2)        AS max_order_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.return_flag = 'N'
GROUP BY c.segment
ORDER BY average_order_value DESC;

-- AOV by product category
SELECT
    product_category,
    COUNT(order_id)                     AS total_orders,
    ROUND(SUM(order_value), 2)          AS total_revenue,
    ROUND(AVG(order_value), 2)          AS average_order_value
FROM orders
WHERE return_flag = 'N'
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Monthly AOV trend
SELECT
    DATE_TRUNC('month', order_date)     AS month,
    COUNT(order_id)                     AS total_orders,
    ROUND(SUM(order_value), 2)          AS monthly_revenue,
    ROUND(AVG(order_value), 2)          AS monthly_aov
FROM orders
WHERE return_flag = 'N'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;


-- ============================================================
-- 2. REPEAT PURCHASE RATE
--    % of customers who placed more than one order
-- ============================================================
WITH purchase_counts AS (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count
    FROM orders
    WHERE return_flag = 'N'
    GROUP BY customer_id
)
SELECT
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)               AS repeat_customers,
    SUM(CASE WHEN order_count = 1 THEN 1 ELSE 0 END)               AS one_time_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                               AS repeat_purchase_rate_pct
FROM purchase_counts;

-- Repeat purchase rate by segment
WITH purchase_counts AS (
    SELECT
        c.customer_id,
        c.segment,
        COUNT(o.order_id) AS order_count
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.return_flag = 'N'
    GROUP BY c.customer_id, c.segment
)
SELECT
    segment,
    COUNT(*)                                                            AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)                   AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                                   AS repeat_purchase_rate_pct,
    ROUND(AVG(order_count), 2)                                          AS avg_orders_per_customer
FROM purchase_counts
GROUP BY segment
ORDER BY repeat_purchase_rate_pct DESC;


-- ============================================================
-- 3. CUSTOMER LIFETIME VALUE (CLV)
--    Historical CLV = total spend per customer
--    Predictive CLV = avg_order_value * purchase_frequency * avg_customer_lifespan
-- ============================================================

-- Historical CLV per customer
SELECT
    c.customer_id,
    c.name,
    c.segment,
    COUNT(o.order_id)                                   AS total_orders,
    ROUND(SUM(o.order_value), 2)                        AS historical_clv,
    ROUND(AVG(o.order_value), 2)                        AS avg_order_value,
    MIN(o.order_date)                                   AS first_purchase,
    MAX(o.order_date)                                   AS last_purchase,
    MAX(o.order_date) - MIN(o.order_date)               AS customer_lifespan_days
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.return_flag = 'N'
GROUP BY c.customer_id, c.name, c.segment
ORDER BY historical_clv DESC;

-- Predictive CLV (simple model over 12 months)
-- Formula: CLV = AOV × Purchase_Frequency_per_month × 12
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.name,
        c.segment,
        COUNT(o.order_id)                               AS total_orders,
        ROUND(SUM(o.order_value), 2)                    AS total_revenue,
        ROUND(AVG(o.order_value), 2)                    AS avg_order_value,
        NULLIF(MAX(o.order_date) - MIN(o.order_date), 0) AS lifespan_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.return_flag = 'N'
    GROUP BY c.customer_id, c.name, c.segment
)
SELECT
    customer_id,
    name,
    segment,
    total_orders,
    total_revenue,
    avg_order_value,
    lifespan_days,
    -- Monthly purchase frequency
    ROUND(COALESCE(total_orders * 30.0 / NULLIF(lifespan_days, 0), 0), 3) AS monthly_freq,
    -- Projected 12-month CLV
    ROUND(
        avg_order_value
        * COALESCE(total_orders * 30.0 / NULLIF(lifespan_days, 0), total_orders)
        * 12, 2
    )                                                   AS predicted_clv_12m
FROM customer_metrics
ORDER BY predicted_clv_12m DESC;

-- Average CLV by segment
WITH customer_clv AS (
    SELECT
        c.segment,
        c.customer_id,
        SUM(o.order_value) AS total_revenue
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.return_flag = 'N'
    GROUP BY c.segment, c.customer_id
)
SELECT
    segment,
    COUNT(customer_id)              AS customers,
    ROUND(AVG(total_revenue), 2)    AS avg_clv,
    ROUND(SUM(total_revenue), 2)    AS total_segment_revenue,
    ROUND(MIN(total_revenue), 2)    AS min_clv,
    ROUND(MAX(total_revenue), 2)    AS max_clv
FROM customer_clv
GROUP BY segment
ORDER BY avg_clv DESC;


-- ============================================================
-- 4. MONTHLY ACTIVE CUSTOMERS
-- ============================================================
SELECT
    DATE_TRUNC('month', order_date)     AS month,
    COUNT(DISTINCT customer_id)         AS monthly_active_customers,
    COUNT(order_id)                     AS total_orders,
    ROUND(SUM(order_value), 2)          AS monthly_revenue
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;


-- ============================================================
-- 5. REVENUE BY PRODUCT CATEGORY AND SEGMENT
-- ============================================================
SELECT
    o.product_category,
    c.segment,
    COUNT(DISTINCT o.customer_id)       AS unique_customers,
    COUNT(o.order_id)                   AS total_orders,
    ROUND(SUM(o.order_value), 2)        AS total_revenue,
    ROUND(AVG(o.order_value), 2)        AS avg_order_value
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
WHERE o.return_flag = 'N'
GROUP BY o.product_category, c.segment
ORDER BY total_revenue DESC;


-- ============================================================
-- 6. TOP 10 CUSTOMERS BY REVENUE
-- ============================================================
SELECT
    c.customer_id,
    c.name,
    c.segment,
    c.location,
    COUNT(o.order_id)                   AS total_orders,
    ROUND(SUM(o.order_value), 2)        AS total_revenue,
    ROUND(AVG(o.order_value), 2)        AS avg_order_value,
    MAX(o.order_date)                   AS last_purchase_date
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.return_flag = 'N'
GROUP BY c.customer_id, c.name, c.segment, c.location
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 7. DISCOUNT IMPACT ON ORDER VALUE AND CHURN
-- ============================================================
SELECT
    CASE
        WHEN discount_pct = 0          THEN '0% (No Discount)'
        WHEN discount_pct BETWEEN 1 AND 9   THEN '1-9%'
        WHEN discount_pct BETWEEN 10 AND 14 THEN '10-14%'
        WHEN discount_pct >= 15        THEN '15%+'
    END                                     AS discount_bucket,
    COUNT(DISTINCT customer_id)             AS unique_customers,
    COUNT(order_id)                         AS total_orders,
    ROUND(AVG(order_value), 2)              AS avg_order_value,
    ROUND(SUM(order_value), 2)              AS total_revenue
FROM orders
WHERE return_flag = 'N'
GROUP BY discount_bucket
ORDER BY avg_order_value DESC;


-- ============================================================
-- 8. RETURN RATE BY CATEGORY
-- ============================================================
SELECT
    product_category,
    COUNT(order_id)                                             AS total_orders,
    SUM(CASE WHEN return_flag = 'Y' THEN 1 ELSE 0 END)         AS returns,
    ROUND(
        100.0 * SUM(CASE WHEN return_flag = 'Y' THEN 1 ELSE 0 END)
        / COUNT(order_id), 2
    )                                                           AS return_rate_pct
FROM orders
GROUP BY product_category
ORDER BY return_rate_pct DESC;
