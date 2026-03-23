WITH source AS (
    SELECT * FROM {{ ref('src_student_performance') }}
),
renamed AS (
    SELECT
        "gender" as gender,
        "race/ethnicity" as race_ethnicity,
        "parental level of education" as parental_education,
        "lunch" as lunch,
        "test preparation course" as test_prep,
        CAST("math score" AS INTEGER) as math_score,
        CAST("reading score" AS INTEGER) as reading_score,
        CAST("writing score" AS INTEGER) as writing_score,
        (CAST("math score" AS INTEGER) + CAST("reading score" AS INTEGER) + CAST("writing score" AS INTEGER)) as total_score,
        ROUND((CAST("math score" AS INTEGER) + CAST("reading score" AS INTEGER) + CAST("writing score" AS INTEGER)) / 3.0, 2) as average_score
    FROM source
)

SELECT * FROM renamed
