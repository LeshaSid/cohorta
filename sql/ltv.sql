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
SELECT 
    ci.cohort_date,
    ci.period_number,
    COUNT(DISTINCT ci.user_id) AS user_count,
    COALESCE(SUM((e.properties->>'revenue')::numeric), 0) AS revenue_sum
FROM cohort_interval ci
LEFT JOIN events e 
    ON ci.user_id = e.user_id
    AND DATE(e.timestamp_event) = DATE(ci.cohort_date + ci.period_number)
    AND e.event_name = 'purchase'
GROUP BY ci.cohort_date, ci.period_number
ORDER BY ci.cohort_date, ci.period_number