from rejson.path import Path
import pytz
from utils.client import get_redis_client
from datetime import datetime

from utils.mail import send_email
from celery import Celery
import requests
import os

APP_NAME = 'tasks'
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
BROKER_NAME = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'

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
    IST = pytz.timezone('Asia/Kolkata')
    date = datetime.now(IST).strftime("%d-%m-%Y")
    params = {"district_id": district_id, "date": date}
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    centers = requests.get(url, params=params, headers=headers)
    centers = centers.json()
    emails = client.jsonget("districts", Path(f'["{district_id}"]'))
    paths = [Path(f'["{email}"]') for email in emails]
    users = client.jsonget("users", *paths)
    for center in centers['centers']:
        for session in center['sessions']:
            if session['min_age_limit'] > 0:
                tb_notified_users = []
                session_id = session['session_id']
                if len(emails) == 1:
                    if session_id not in users['session_ids']:
                        if users['verified']:
                            email = users['email']
                            tb_notified_users.append(email)
                            client.jsonarrappend("users", Path(f'["{email}"]["session_ids"]'), session_id)
                else:
                    for user in users.values():
                        if user['verified']:
                            if session_id not in user['session_ids']:
                                email = user['email']
                                tb_notified_users.append(email)
                                client.jsonarrappend("users", Path(f'["{email}"]["session_ids"]'), session_id)
                subject = "COWIN Vaccine Slots alert"
                body = f'''
                Slots have opened up for your district, {center['district_name']}. Please check the given details below:
                Center Name: {center['name']}
                Date: {session['date']}
                From: {center['from']}
                To: {center['to']}

                Please book your vaccination slot now. Stay safe!
                '''
                send_email(tb_notified_users, subject, body)
