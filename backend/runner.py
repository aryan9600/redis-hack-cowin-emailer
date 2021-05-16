from worker.tasks import fetch_slots
from utils.client import get_redis_client
import time


client = get_redis_client()
while True:
    district_ids = client.jsonobjkeys("districts")
    for district_id in district_ids:
        district_id = int(district_id)
        fetch_slots.delay(district_id)
    time.sleep(90)
