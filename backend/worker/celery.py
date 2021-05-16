from celery import Celery

APP_NAME = 'worker'
BROKER_NAME = 'redis://:NworrNgcOZkR4Alna0RUgeQL3nf2kqAP@redis-17210.c232.us-east-1-2.ec2.cloud.redislabs.com:17210'

app = Celery(APP_NAME, broker=BROKER_NAME, include=['worker.tasks'])
