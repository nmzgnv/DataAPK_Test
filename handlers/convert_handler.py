import json

from aiohttp import web
from aiohttp_pydantic import PydanticView

from handlers.utils import get_error_response

from aiohttp_pydantic.injectors import Group
from pydantic import Field


class ConvertHandlerModel(Group):
    from_: str = Field(alias='from')
    to: str
    amount: float = Field(ge=0)


class ConvertHandler(PydanticView):
    async def get(self, conversion: ConvertHandlerModel):
        db = self.request.app.get('db')
        conversions = await db.execute_command('get', conversion.from_)

        if not conversions:
            return get_error_response('FROM currency not found')

        conversions_json = json.loads(conversions)

        if conversion.to not in conversions_json.keys():
            return get_error_response('TO currency not found')

        return web.json_response({
            'value': conversions_json.get(conversion.to) * conversion.amount,
        })
