SELECT
    store_id,
    store_name,
    city,
    country,
    store_type
FROM {{ ref('src_stores') }}
