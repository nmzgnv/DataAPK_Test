import json

from aiohttp.test_utils import AioHTTPTestCase
from aioredis import Redis

from main import init_app


class ConvertHandlerTest(AioHTTPTestCase):
    async def get_application(self):
        app = await init_app()
        self.db: Redis = app['db']

        self.TEST_KEY_FROM = 'TEST_NOT_EXIST'
        self.TEST_KEY_TO = 'TEST_TO'
        self.TEST_EXCHANGE_RATE = 0.1

        return app

    async def tearDownAsync(self):
        await self.db.connection_pool.disconnect()
        await self.app.shutdown()
        await super().tearDownAsync()

    async def case_test(self, request_body, expected_status, expected_answer):
        async with self.client.post('/database', json=request_body) as resp:
            self.assertEqual(expected_answer, await resp.json())
            self.assertEqual(expected_status, resp.status)
            self.assertEqual("application/json", resp.content_type)

    async def test_database_invalid_body_of_request(self):
        body = {
            'merge': 1,
            'data': "data"
        }

        await self.case_test(body, 400, [{
            "loc": [
                "data"
            ],
            "msg": "value is not a valid list",
            "type": "type_error.list",
            "in": "body"
        }])

    async def test_database_exchange_rate_lower_or_equal_0(self):
        for ex_rate in (-1, 0):
            body = {
                'merge': 1,
                'data': [{
                    'from': 'RUB',
                    'to': 'UAH',
                    'exchange_rate': ex_rate
                }]
            }

            await self.case_test(body, 400, [{'ctx': {'limit_value': 0},
                                              'in': 'body',
                                              'loc': ['data', 0, 'exchange_rate'],
                                              'msg': 'ensure this value is greater than 0',
                                              'type': 'value_error.number.not_gt'}])

    async def test_database_add_data_when_not_exist(self):
        await self.db.delete(self.TEST_KEY_FROM)

        body = {
            'merge': 1,
            'data': [{
                'from': self.TEST_KEY_FROM,
                'to': self.TEST_KEY_TO,
                'exchange_rate': self.TEST_EXCHANGE_RATE
            }]
        }

        await self.case_test(body, 200,
                             {
                                 'data': [
                                     f'{{"from_": "{self.TEST_KEY_FROM}", "to": "{self.TEST_KEY_TO}", '
                                     f'"exchange_rate": {self.TEST_EXCHANGE_RATE}}}'
                                 ]
                             })

        data = await self.db.get(self.TEST_KEY_FROM)
        data = json.loads(data)
        self.assertEqual(self.TEST_EXCHANGE_RATE, data.get(self.TEST_KEY_TO))

    async def test_database_overwrite_data_when_exist(self):
        await self.db.execute_command('set', self.TEST_KEY_FROM,
                                      json.dumps({self.TEST_KEY_TO: self.TEST_EXCHANGE_RATE}))
        new_exchange_rate = 10.1
        body = {
            'merge': 1,
            'data': [{
                'from': self.TEST_KEY_FROM,
                'to': self.TEST_KEY_TO,
                'exchange_rate': new_exchange_rate
            }]
        }

        await self.case_test(body, 200,
                             {
                                 'data': [
                                     f'{{"from_": "{self.TEST_KEY_FROM}", "to": "{self.TEST_KEY_TO}", '
                                     f'"exchange_rate": {new_exchange_rate}}}'
                                 ]
                             })
        data = await self.db.get(self.TEST_KEY_FROM)
        data = json.loads(data)
        self.assertEqual(new_exchange_rate, data.get(self.TEST_KEY_TO))

        await self.db.delete(self.TEST_KEY_FROM)

    async def test_database_add_data_when_merge_is_1(self):
        await self.db.execute_command('set', self.TEST_KEY_FROM,
                                      json.dumps({self.TEST_KEY_TO: self.TEST_EXCHANGE_RATE}))
        new_test_to = 'TEST_TO_2'
        exchange_rate = 1.2
        body = {
            'merge': 1,
            'data': [{
                'from': self.TEST_KEY_FROM,
                'to': new_test_to,
                'exchange_rate': exchange_rate
            }]
        }

        # validate answer
        await self.case_test(body, 200,
                             {
                                 'data': [
                                     f'{{"from_": "{self.TEST_KEY_FROM}", "to": "{new_test_to}", '
                                     f'"exchange_rate": {exchange_rate}}}'
                                 ]
                             })
        # validate db
        data = await self.db.get(self.TEST_KEY_FROM)
        data = json.loads(data)
        self.assertEqual({
            self.TEST_KEY_TO: self.TEST_EXCHANGE_RATE,
            new_test_to: exchange_rate,
        }, data)

        await self.db.delete(self.TEST_KEY_FROM)

    async def test_database_save_only_new_data_when_merge_is_0(self):
        await self.db.execute_command('set', self.TEST_KEY_FROM,
                                      json.dumps({
                                          self.TEST_KEY_TO: self.TEST_EXCHANGE_RATE,
                                          'test_key_to_2': 99123.1
                                      }))
        new_exchange_rate = 10 + self.TEST_EXCHANGE_RATE
        body = {
            'merge': 0,
            'data': [{
                'from': self.TEST_KEY_FROM,
                'to': self.TEST_KEY_TO,
                'exchange_rate': new_exchange_rate,
            }]
        }

        # validate answer
        await self.case_test(body, 200,
                             {
                                 'data': [
                                     f'{{"from_": "{self.TEST_KEY_FROM}", "to": "{self.TEST_KEY_TO}", '
                                     f'"exchange_rate": {new_exchange_rate}}}'
                                 ]
                             })
        # validate db
        data = await self.db.get(self.TEST_KEY_FROM)
        data = json.loads(data)
        self.assertEqual({self.TEST_KEY_TO: new_exchange_rate}, data)

        await self.db.delete(self.TEST_KEY_FROM)
