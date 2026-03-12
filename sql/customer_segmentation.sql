-- ============================================================
-- E-Commerce Customer Churn Analysis – Customer Segmentation
-- RFM (Recency, Frequency, Monetary) Analysis
-- ============================================================

-- Analysis reference date (last day of data)
-- Adjust ':analysis_date' to CURRENT_DATE for live queries
-- ============================================================

-- ============================================================
-- STEP 1: Calculate raw RFM metrics per customer
-- ============================================================
WITH rfm_raw AS (
    SELECT
        c.customer_id,
        c.name,
        c.segment                                                AS original_segment,
        c.location,
        MAX(o.order_date)                                       AS last_purchase_date,
        COUNT(DISTINCT o.order_id)                              AS frequency,
        ROUND(SUM(o.order_value), 2)                            AS monetary,
        CURRENT_DATE - MAX(o.order_date)                        AS recency_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.return_flag = 'N'                                   -- exclude returned orders
    GROUP BY c.customer_id, c.name, c.segment, c.location
),

-- ============================================================
-- STEP 2: Assign RFM scores (1–5) using quintile ranking
-- Higher score = better customer behaviour
-- ============================================================
rfm_scores AS (
    SELECT
        *,
        -- Recency: lower days = better = higher score
        NTILE(5) OVER (ORDER BY recency_days DESC)  AS r_score,
        -- Frequency: more orders = better = higher score
        NTILE(5) OVER (ORDER BY frequency ASC)      AS f_score,
        -- Monetary: higher spend = better = higher score
        NTILE(5) OVER (ORDER BY monetary ASC)       AS m_score
    FROM rfm_raw
),

-- ============================================================
-- STEP 3: Composite RFM score and string label
-- ============================================================
rfm_combined AS (
    SELECT
        *,
        (r_score + f_score + m_score)                           AS rfm_total,
        CONCAT(r_score, f_score, m_score)                       AS rfm_cell
    FROM rfm_scores
)

-- ============================================================
-- STEP 4: Map RFM scores to customer segments / tiers
-- ============================================================
SELECT
    customer_id,
    name,
    original_segment,
    location,
    last_purchase_date,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    rfm_total,
    rfm_cell,
    CASE
        -- Champions: bought recently, buy often, spend the most
        WHEN r_score = 5 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        -- Loyal Customers: buy regularly and recently
        WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        -- Potential Loyalists: recent customers with average frequency
        WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Potential Loyalists'
        -- Recent Customers: bought recently but not often
        WHEN r_score >= 4 AND f_score <= 2                    THEN 'Recent Customers'
        -- Promising: recent, low frequency, low spend
        WHEN r_score = 3 AND f_score <= 2                    THEN 'Promising'
        -- Needs Attention: above average recency and frequency but not recent
        WHEN r_score = 2 AND f_score >= 3 AND m_score >= 3  THEN 'Needs Attention'
        -- About to Sleep: below average recency
        WHEN r_score = 2 AND f_score <= 2                    THEN 'About to Sleep'
        -- At Risk: spent big money, purchased often, but long ago
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk'
        -- Cannot Lose Them: made largest purchases but haven't returned
        WHEN r_score = 1 AND f_score >= 3 AND m_score >= 4  THEN 'Can''t Lose Them'
ORDER BY rfm_total DESC;


-- ============================================================
-- Segment Summary: count and average metrics per RFM tier
-- ============================================================
WITH rfm_raw AS (
    SELECT
        c.customer_id,
        MAX(o.order_date)                  AS last_purchase_date,
        COUNT(DISTINCT o.order_id)         AS frequency,
        ROUND(SUM(o.order_value), 2)       AS monetary,
        CURRENT_DATE - MAX(o.order_date)   AS recency_days
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.return_flag = 'N'
    GROUP BY c.customer_id
),
rfm_scores AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM rfm_raw
),
rfm_segments AS (
    SELECT *,
        CASE
            WHEN r_score = 5 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score <= 2                  THEN 'Recent Customers'
            WHEN r_score = 3 AND f_score <= 2                   THEN 'Promising'
            WHEN r_score = 2 AND f_score >= 3 AND m_score >= 3  THEN 'Needs Attention'
            WHEN r_score = 2 AND f_score <= 2                   THEN 'About to Sleep'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'At Risk'
            WHEN r_score = 1 AND f_score >= 3 AND m_score >= 4  THEN 'Can''t Lose Them'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Hibernating'
            ELSE 'Lost'
        END AS rfm_segment
    FROM rfm_scores
)
SELECT
    rfm_segment,
    COUNT(*)                        AS customer_count,
    ROUND(AVG(recency_days), 1)    AS avg_recency_days,
    ROUND(AVG(frequency), 1)       AS avg_frequency,
    ROUND(AVG(monetary), 2)        AS avg_monetary,
    ROUND(SUM(monetary), 2)        AS total_revenue
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_revenue DESC;
