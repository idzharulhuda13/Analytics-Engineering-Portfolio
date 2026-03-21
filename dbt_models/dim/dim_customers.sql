SELECT
    customer_id,
    age,
    CASE 
        WHEN age < 18 THEN 'Under 18'
        WHEN age BETWEEN 18 AND 24 THEN '18-24'
        WHEN age BETWEEN 25 AND 34 THEN '25-34'
        WHEN age BETWEEN 35 AND 44 THEN '35-44'
        WHEN age BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END AS age_group,
    gender,
    loyalty_member,
    CASE WHEN loyalty_member = 1 THEN 'Yes' ELSE 'No' END AS is_loyalty_member_text,
    join_date
FROM {{ ref('src_customers') }}
