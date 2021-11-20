import asyncio
import aioredis
from aiohttp import web
from config import REDIS_HOST, REDIS_PORT, HOST, PORT
from handlers.convert_handler import ConvertHandler
from handlers.database_handler import DatabaseHandler


async def init_app():
    app = web.Application()
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)
    app['db'] = redis
    app.router.add_view('/convert', ConvertHandler)
    app.router.add_view('/database', DatabaseHandler)
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host=HOST, port=PORT)
