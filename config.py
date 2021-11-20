import os

REDIS_URL = f"redis://127.0.0.1:6379"

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8000))
