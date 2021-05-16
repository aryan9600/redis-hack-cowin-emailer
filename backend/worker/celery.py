import os
from celery import Celery

APP_NAME = 'worker'
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_HOST = os.environ['REDIS_HOST']
BROKER_NAME = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'


app = Celery(APP_NAME, broker=BROKER_NAME, include=['worker.tasks'])
