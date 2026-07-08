from datetime import datetime, timedelta, time
import numpy as np
import random
import itertools
import psycopg2
from psycopg2 import extras
import json

user_id_counter = itertools.count(1)
def generate_user():
    user_id = next(user_id_counter)
    device_type = random.choices(["Mobile", "Desktop"], [0.65, 0.35])[0]
    traffic_source = random.choices(["Organic", "Social", "Referral"], [0.45, 0.35, 0.2])[0]
    return user_id, device_type, traffic_source

def count_of_users_per_day(current_datetime):
    base = int(random.normalvariate(10000, 1500))
    if 0 <= current_datetime.weekday() <= 3:
        k = 0.8
    elif current_datetime.weekday() == 4:
        k = 1.1
    else:
        k = 1.3
    return base * k

def generate_data():
    all_events = []
    all_ab_exposures = []
    user_groups = {}
    retention_users = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    current_date = start_date
    while current_date <= end_date:
        n = count_of_users_per_day(current_date)
        for i in range(n):
            if retention_users and random.random() < 0.4:
                user = random.choice(retention_users)
                if random.random() < min(0.1*(np.sqrt(user[3])), 1):
                    user_id = user[0]
                    device_type = user[1]
                    traffic_source = user[2]
                    user[3] += 1
                else:
                    user_id, device_type, traffic_source = generate_user()
                    if random.random() < 0.3:
                        retention_users.append([user_id, device_type, traffic_source, 1])
            else:
                user_id, device_type, traffic_source = generate_user()
                if random.random() < 0.3:
                    retention_users.append([user_id, device_type, traffic_source, 1])
            user_events = []
            hour = max(0, min(int(random.normalvariate(20, 2)), 23))
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp_event = datetime.combine(current_date, time(hour, minute, second))
            user_events.append({
                "timestamp_event": timestamp_event,
                "user_id": user_id,
                "anonymous_id": f"anon_{user_id}",
                "event_name": "view_product",
                "device_type": device_type,
                "traffic_source": traffic_source,
                "properties": {}
            })
            if user_id in user_groups:
                group = user_groups[user_id]
            else:
                group = random.choice(["A", "B"])
                user_groups[user_id] = group
                all_ab_exposures.append({
                    "user_id" : user_id,
                    "timestamp_ab" : timestamp_event,
                    "experiment_name" : "cart_discount",
                    "group_ab" : group
                })
            if random.random() < 0.3:
                timestamp_event += timedelta(minutes=random.randint(1, 15))
                user_events.append({
                    "timestamp_event": timestamp_event,
                    "user_id": user_id,
                    "anonymous_id": f"anon_{user_id}",
                    "event_name": "add_to_cart",
                    "device_type": device_type,
                    "traffic_source": traffic_source,
                    "properties": {}
                })
                match group:
                    case "B":
                        p = 0.22
                        sale = 0.85
                    case _:
                        p = 0.15
                        sale = 1
                
                if random.random() < p:
                    timestamp_event += timedelta(minutes=random.randint(1, 15))
                    user_events.append({
                    "timestamp_event": timestamp_event,
                    "user_id": user_id,
                    "anonymous_id": f"anon_{user_id}",
                    "event_name": "purchase",
                    "device_type": device_type,
                    "traffic_source": traffic_source,
                    "properties": {
                        "revenue" : random.randint(500, 5000) * sale,
                        "category" : random.choice(["electronics", "health & beauty", "home & garden", "apparel & accessories", "groceries", "toys, hobbies & diy"])
                    }
                })
            all_events.extend(user_events)
        current_date += timedelta(days=1)
    return all_events, all_ab_exposures

def save_to_db(events, ab_exposures):
    conn = psycopg2.connect(
        host = "localhost",
        port = 5433,
        dbname = "cohorta_db",
        user = "postgres",
        password = "postgres"
    )
    cursor = conn.cursor()
    for event in events:
        event["properties"] = json.dumps(event["properties"])

    query_events = """
    INSERT INTO events (timestamp_event, user_id, anonymous_id, event_name, device_type, traffic_source, properties)
    VALUES (%(timestamp_event)s, %(user_id)s, %(anonymous_id)s, %(event_name)s, %(device_type)s, %(traffic_source)s, %(properties)s)
    """

    query_ab = """
    INSERT INTO ab_exposures (user_id, timestamp_ab, experiment_name, group_ab)
    VALUES (%(user_id)s, %(timestamp_ab)s, %(experiment_name)s, %(group_ab)s)
    """

    try:
        extras.execute_batch(cursor, query_events, events, page_size=10000)
        extras.execute_batch(cursor, query_ab, ab_exposures, page_size=10000)
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    events, ab_exposures = generate_data()
    save_to_db(events, ab_exposures)