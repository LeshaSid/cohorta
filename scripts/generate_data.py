import random

user_id_global = -1
def generate_user():
    user_id += user_id_global
    user_id_global += 1

    device_type = random.choices(["Mobile", "Desktop"], [0.65, 0.35])
    traffic_source = random.choices(["Organic", "Social", "Referral"], [0.45, 0.35, 0.2])

def count_of_users_per_day(datetime):
    pass

def main():
    pass
