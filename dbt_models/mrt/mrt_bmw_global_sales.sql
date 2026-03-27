WITH source AS (
    SELECT * FROM {{ ref('src_bmw_global_sales') }}
),
renamed AS (
    SELECT
        CAST("Year" AS INTEGER) AS year,
        CAST("Month" AS INTEGER) AS month,
        "Region" AS region,
        "Model" AS model,
        CAST("Units_Sold" AS INTEGER) AS units_sold,
        CAST("Avg_Price_EUR" AS DOUBLE) AS avg_price_eur,
        CAST("Revenue_EUR" AS DOUBLE) AS revenue_eur,
        CAST("BEV_Share" AS DOUBLE) AS bev_share,
        CAST("Premium_Share" AS DOUBLE) AS premium_share,
        CAST("GDP_Growth" AS DOUBLE) AS gdp_growth,
        CAST("Fuel_Price_Index" AS DOUBLE) AS fuel_price_index,
        CASE WHEN "Model" IN ('i4', 'iX') THEN TRUE ELSE FALSE END AS is_bev,
        ROUND(CAST("Revenue_EUR" AS DOUBLE) / 1e9, 4) AS revenue_eur_b
    FROM source
)

SELECT * FROM renamed
