from aiohttp import web
from aiohttp_pydantic import PydanticView
from pydantic import BaseModel, Field

from handlers.utils import get_error_json


class DatabaseHandlerModel(BaseModel):
    merge: int = Field(ge=0, le=1)


class DatabaseHandler(PydanticView):
    async def post(self, params: DatabaseHandlerModel):
        print(params)
        return web.json_response({'name': 'good'})
