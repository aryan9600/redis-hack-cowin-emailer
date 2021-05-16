import os
from rejson import Client, Path


def get_redis_client():
    client = Client(
        host=os.environ['REDIS_HOST'],
        port=os.environ['REDIS_PORT'],
        password=os.os.environ['REDIS_PASSWORD'],
        decode_responses=True,
        db=0
    )
    if client.exists("districts") == 0:
        client.jsonset("districts", Path.rootPath(), {})
    if client.exists("users") == 0:
        client.jsonset("users", Path.rootPath(), {})
    return client

