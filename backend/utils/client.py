from rejson import Client, Path
import os


def get_redis_client():
    REDIS_PORT = os.environ['REDIS_PORT']
    REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
    REDIS_HOST = os.environ['REDIS_HOST']
    client = Client(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
    if client.exists("districts") == 0:
        client.jsonset("districts", Path.rootPath(), {})
    if client.exists("users") == 0:
        client.jsonset("users", Path.rootPath(), {})
    return client

