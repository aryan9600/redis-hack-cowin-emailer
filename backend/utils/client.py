from rejson import Client, Path


def get_redis_client():
    client = Client(
        host='redis-17210.c232.us-east-1-2.ec2.cloud.redislabs.com',
        port=17210,
        password='NworrNgcOZkR4Alna0RUgeQL3nf2kqAP',
        decode_responses=True
    )
    if client.exists("districts") == 0:
        client.jsonset("districts", Path.rootPath(), {})
    if client.exists("users") == 0:
        client.jsonset("users", Path.rootPath(), {})
    return client

