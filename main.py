import asyncio
import json
import aioredis
from aiohttp import web
from aiohttp_pydantic import PydanticView
from config import REDIS_HOST, REDIS_PORT, HOST, PORT
from models import DatabaseHandlerModel, ConvertHandlerModel


class ConvertHandler(PydanticView):
    async def get(self, conversion: ConvertHandlerModel):
        db = self.request.app.get('db')
        conversions = await db.execute_command('get', conversion.from_)

        if not conversions:
            return web.json_response({'error': 'FROM currency not found'}, status=400)

        conversions_json = json.loads(conversions)

        if conversion.to not in conversions_json.keys():
            return web.json_response({'error': 'TO currency not found'}, status=400)

        return web.json_response({
            'value': conversions_json.get(conversion.to) * conversion.amount,
        })


class DatabaseHandler(PydanticView):
    async def post(self, params: DatabaseHandlerModel):
        print(params)
        return web.json_response({'name': 'good'})


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
