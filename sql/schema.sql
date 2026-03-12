-- ============================================================
-- E-Commerce Customer Churn Analysis – Database Schema
-- Compatible with PostgreSQL 13+ and MySQL 8+
-- ============================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ============================================================
-- CUSTOMERS TABLE
-- ============================================================
CREATE TABLE customers (
    customer_id   VARCHAR(10)  PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    signup_date   DATE         NOT NULL,
    location      VARCHAR(100),
    segment       VARCHAR(20)  CHECK (segment IN ('Premium', 'Regular', 'Occasional', 'New'))
);

-- Index for segmentation queries
CREATE INDEX idx_customers_segment   ON customers (segment);
CREATE INDEX idx_customers_signup    ON customers (signup_date);
CREATE INDEX idx_customers_location  ON customers (location);

-- ============================================================
-- PRODUCTS TABLE
-- ============================================================
CREATE TABLE products (
    product_id       VARCHAR(10)    PRIMARY KEY,
    product_name     VARCHAR(200)   NOT NULL,
    category         VARCHAR(50)    NOT NULL,
    unit_price       DECIMAL(10, 2) NOT NULL,
    cost_price       DECIMAL(10, 2),
    stock_quantity   INT            DEFAULT 0
);

CREATE INDEX idx_products_category ON products (category);

-- ============================================================
-- ORDERS TABLE
-- ============================================================
CREATE TABLE orders (
    order_id        VARCHAR(10)    PRIMARY KEY,
    customer_id     VARCHAR(10)    NOT NULL REFERENCES customers (customer_id),
    order_date      DATE           NOT NULL,
    order_value     DECIMAL(10, 2) NOT NULL CHECK (order_value >= 0),
    product_category VARCHAR(50),
    quantity        INT            DEFAULT 1 CHECK (quantity > 0),
    discount_pct    DECIMAL(5, 2)  DEFAULT 0 CHECK (discount_pct >= 0 AND discount_pct <= 100),
    payment_method  VARCHAR(30),
    return_flag     CHAR(1)        DEFAULT 'N' CHECK (return_flag IN ('Y', 'N'))
);

CREATE INDEX idx_orders_customer    ON orders (customer_id);
CREATE INDEX idx_orders_date        ON orders (order_date);
CREATE INDEX idx_orders_category    ON orders (product_category);
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- ============================================================
-- ORDER ITEMS TABLE (normalised detail – optional extension)
-- ============================================================
CREATE TABLE order_items (
    item_id        SERIAL         PRIMARY KEY,
    order_id       VARCHAR(10)    NOT NULL REFERENCES orders (order_id),
    product_id     VARCHAR(10)    REFERENCES products (product_id),
    quantity       INT            NOT NULL CHECK (quantity > 0),
    unit_price     DECIMAL(10, 2) NOT NULL,
    discount_pct   DECIMAL(5, 2)  DEFAULT 0,
    line_total     DECIMAL(10, 2) GENERATED ALWAYS AS
                       (unit_price * quantity * (1 - discount_pct / 100)) STORED
);

CREATE INDEX idx_order_items_order   ON order_items (order_id);
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- ============================================================
-- HELPER VIEW – flat customer transaction summary
-- ============================================================
CREATE OR REPLACE VIEW customer_order_summary AS
SELECT
    c.customer_id,
    c.name,
    c.segment,
    c.location,
    c.signup_date,
    COUNT(o.order_id)                               AS total_orders,
    SUM(o.order_value)                              AS total_revenue,
    ROUND(AVG(o.order_value), 2)                    AS avg_order_value,
    MIN(o.order_date)                               AS first_order_date,
    MAX(o.order_date)                               AS last_order_date,
    CURRENT_DATE - MAX(o.order_date)                AS days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id, c.name, c.segment, c.location, c.signup_date;
