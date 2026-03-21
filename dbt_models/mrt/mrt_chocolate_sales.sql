{{ config(materialized='table') }}

SELECT
    s.order_id,
    s.order_date,
    s.product_id,
    s.store_id,
    s.customer_id,
    s.quantity,
    s.unit_price,
    s.discount,
    s.revenue,
    s.cost,
    s.profit,
    
    -- Product details
    p.product_name,
    p.brand,
    p.category,
    p.cocoa_percent,
    p.cocoa_category,
    p.weight_g,
    
    -- Customer details
    c.age AS customer_age,
    c.age_group AS customer_age_group,
    c.gender AS customer_gender,
    c.is_loyalty_member_text AS is_loyalty_member,
    c.join_date AS customer_join_date,
    
    -- Store details
    st.store_name,
    st.city AS store_city,
    st.country AS store_country,
    st.store_type,
    
    -- Calendar details
    cal.year,
    cal.quarter,
    cal.month,
    cal.day,
    cal.week,
    cal.day_of_week,
    cal.is_weekend
    
FROM {{ ref('src_sales') }} s
LEFT JOIN {{ ref('dim_products') }} p
    ON s.product_id = p.product_id
LEFT JOIN {{ ref('dim_customers') }} c
    ON s.customer_id = c.customer_id
LEFT JOIN {{ ref('dim_stores') }} st
    ON s.store_id = st.store_id
LEFT JOIN {{ ref('dim_calendar') }} cal
    ON s.order_date = cal.date
