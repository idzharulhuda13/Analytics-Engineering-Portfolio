SELECT
    date,
    year,
    month,
    day,
    week,
    day_of_week,
    CASE WHEN day_of_week IN (6, 7) THEN True ELSE False END as is_weekend,
    CASE 
        WHEN month IN (1, 2, 3) THEN 'Q1'
        WHEN month IN (4, 5, 6) THEN 'Q2'
        WHEN month IN (7, 8, 9) THEN 'Q3'
        ELSE 'Q4'
    END AS quarter
FROM {{ ref('src_calendar') }}
