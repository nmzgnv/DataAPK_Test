import asyncio
import aioredis
from aiohttp import web
from config import HOST, PORT, REDIS_URL
from handlers.convert_handler import ConvertHandler
from handlers.database_handler import DatabaseHandler


async def init_app():
    app = web.Application()
    redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    app['db'] = redis
    app.router.add_view('/convert', ConvertHandler)
    app.router.add_view('/database', DatabaseHandler)
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host=HOST, port=PORT)
