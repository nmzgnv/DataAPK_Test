import os

REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8000))
