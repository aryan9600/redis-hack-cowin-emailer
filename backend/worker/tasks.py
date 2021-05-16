from rejson.path import Path
from utils.client import get_redis_client
from datetime import datetime

from utils.mail import send_email
from celery import Celery
import requests

APP_NAME = 'tasks'
BROKER_NAME = 'redis://:NworrNgcOZkR4Alna0RUgeQL3nf2kqAP@redis-17210.c232.us-east-1-2.ec2.cloud.redislabs.com:17210'

app = Celery(APP_NAME, broker=BROKER_NAME)

@app.task
def send_verification_mail(email: str, code: str):
    email = email
    code = code
    subject = "Verify your email!"
    body = f"""
    Please use the below code to verify yourself and start receiving alerts.
    CODE: {code}
    """

    send_email([email], subject, body)

@app.task
def fetch_slots(district_id: int):
    client = get_redis_client()
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict"
    date = datetime.now().strftime("%d-%m-%Y")
    params = {"distirict_id": district_id, "date": date}
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    centers = requests.get(url, params=params, headers=headers).json()
    emails = client.jsonget("districts", Path(f'["{district_id}"]'))
    paths = [Path(f'["{email}"]') for email in emails]
    users = client.jsonget("users", *paths)
    for center in centers:
        for session in center['sessions']:
            tb_notified_users = []
            session_id = session['session_id']
            for user in users.values():
                if session_id not in user['session_ids']:
                    tb_notified_users.append(user['email'])
                    client.jsonarrappend("users", Path(f'["{user.email}"]["session_ids"]'), session_id)
            subject = "COWIN Vaccine Slots alert"
            body = f'''
            Slots have opened up for your district, {center['district']}. Please check the given details below:
            Center Name: {center['name']}
            Date: {session['date']}
            From: {center['from']}
            To: {center['to']}

            Please book your vaccination slot now. Stay safe!
            '''
            send_email(tb_notified_users, subject, body)
