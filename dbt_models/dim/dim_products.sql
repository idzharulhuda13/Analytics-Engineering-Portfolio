SELECT
    product_id,
    product_name,
    brand,
    category,
    cocoa_percent,
    CASE 
        WHEN cocoa_percent >= 70 THEN 'Dark Chocolate'
        WHEN cocoa_percent >= 50 THEN 'Semi-Sweet'
        WHEN cocoa_percent >= 30 THEN 'Milk Chocolate'
        ELSE 'White/Other'
    END AS cocoa_category,
    weight_g
FROM {{ ref('src_products') }}
