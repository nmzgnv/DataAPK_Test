import json
from typing import List

from aiohttp import web
from aiohttp_pydantic import PydanticView
from pydantic import BaseModel, Field

from handlers.utils import get_error_response


class ExchangeModel(BaseModel):
    from_: str = Field(alias='from')
    to: str
    exchange_rate: float = Field(gt=0)


class DatabaseHandlerModel(BaseModel):
    merge: int = Field(ge=0, le=1)
    data: List[ExchangeModel]


class DatabaseHandler(PydanticView):
    def parse_post_body(self, params: DatabaseHandlerModel) -> dict:
        """
        :param params:
             {
                "merge": 1,
                "data": [{
                    "from": "RUB",
                    "to": "UAH",
                    "exchange_rate": 1
                }]
            }
        :return: dict with combined params
        """
        exchanges_dict = {}
        for exchange in params.data:
            from_ = exchange.from_
            to = exchange.to
            rate = exchange.exchange_rate

            if from_ in exchanges_dict.keys():
                exchanges_dict[from_][to] = rate
            else:
                exchanges_dict[from_] = {to: rate}
        return exchanges_dict

    async def post(self, params: DatabaseHandlerModel):
        db = self.request.app.get('db')
        exchanges_dict = self.parse_post_body(params)

        async with db.pipeline(transaction=True) as pipe:
            for currency in exchanges_dict.keys():
                data_to_save = exchanges_dict[currency]

                if params.merge:
                    old_data = await db.get(currency)
                    if old_data:
                        old_data = json.loads(old_data)
                        old_data.update(data_to_save)
                        data_to_save = old_data

                await pipe.set(currency, json.dumps(data_to_save))

            results = await pipe.execute()
            if not all(results):
                return get_error_response('Transactions to the database failed')

        answer = [i.json() for i in params.data]
        return web.json_response({'data': answer})
