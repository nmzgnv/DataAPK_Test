import json
import asyncio_redis
from aiohttp import web
from aiohttp_pydantic import PydanticView
from config import REDIS_HOST, REDIS_PORT, HOST, PORT
from models import DatabaseHandlerModel, ConvertHandlerModel


class ConvertHandler(PydanticView):
    async def get(self, conversion: ConvertHandlerModel):
        redis = await asyncio_redis.Connection.create(host=REDIS_HOST, port=REDIS_PORT)
        conversions = await redis.get(conversion.from_)

        if not conversions:
            return web.json_response({'error': 'FROM currency not found'}, status=400)

        conversions_json = json.loads(conversions)

        if conversion.to not in conversions_json.keys():
            return web.json_response({'error': 'TO currency not found'}, status=400)

        return web.json_response({
            'value': conversions_json.get(conversion.to) * conversion.amount,
        })


class DatabaseHandler(PydanticView):
    async def post(self, article: DatabaseHandlerModel):
        print(article)
        return web.json_response({'name': 'good'})


app = web.Application()
app.router.add_view('/convert', ConvertHandler)
app.router.add_view('/database', DatabaseHandler)

if __name__ == '__main__':
    web.run_app(app, host=HOST, port=PORT)
