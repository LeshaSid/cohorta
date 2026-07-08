WITH user_cohorts AS (
    SELECT user_id, MIN(DATE(timestamp_event)) AS cohort_date
    FROM events
    GROUP BY user_id
),
user_activity AS (
    SELECT DISTINCT user_id, DATE(timestamp_event) AS activity_date
    FROM events
),
cohort_interval AS (
    SELECT a.user_id, c.cohort_date, (a.activity_date - c.cohort_date) AS period_number
    FROM user_activity AS a
    LEFT JOIN user_cohorts AS c
    ON a.user_id = c.user_id
)

SELECT cohort_date,
COUNT(DISTINCT CASE WHEN period_number = 0 THEN user_id END) AS cohort_size,
COUNT(DISTINCT CASE WHEN period_number = 1 THEN user_id END) AS day_1,
COUNT(DISTINCT CASE WHEN period_number = 2 THEN user_id END) AS day_2,
COUNT(DISTINCT CASE WHEN period_number = 7 THEN user_id END) AS day_7
FROM cohort_interval
GROUP BY cohort_date
ORDER BY cohort_date