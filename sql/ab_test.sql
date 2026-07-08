SELECT
    ab.user_id,
    ab.group_ab,
    COALESCE(SUM((e.properties->>'revenue')::numeric), 0) AS sum_revenue,
    COUNT(e.event_name) AS count_purchases
FROM ab_exposures AS ab
LEFT JOIN events e
    ON ab.user_id = e.user_id
    AND e.event_name = 'purchase'
GROUP BY ab.user_id, ab.group_ab;
