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

SELECT cohort_date, period_number, COUNT(DISTINCT user_id) AS user_count
FROM cohort_interval
GROUP BY cohort_date, period_number
ORDER BY cohort_date, period_number