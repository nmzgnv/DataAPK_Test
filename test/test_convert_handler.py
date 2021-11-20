from aiohttp.test_utils import AioHTTPTestCase

from main import init_app


class ConvertHandlerTest(AioHTTPTestCase):
    async def get_application(self):
        app = await init_app()
        return app

    async def case_test(self, params_url, expected_status, expected_answer):
        async with self.client.request("GET", "/convert" + params_url) as resp:
            self.assertEqual(expected_answer, await resp.json())
            self.assertEqual(expected_status, resp.status)
            self.assertEqual("application/json", resp.content_type)

    async def test_convert_without_params(self):
        await self.case_test("", 400, [
            {
                "loc": [
                    "from"
                ],
                "msg": "field required",
                "type": "value_error.missing",
                "in": "query string"
            },
            {
                "loc": [
                    "to"
                ],
                "msg": "field required",
                "type": "value_error.missing",
                "in": "query string"
            },
            {
                "loc": [
                    "amount"
                ],
                "msg": "field required",
                "type": "value_error.missing",
                "in": "query string"
            }
        ])

    async def test_convert_invalid_from_currency(self):
        await self.case_test("?from=None&to=USD&amount=1", 400, {"error": "FROM currency not found"})

    async def test_convert_invalid_to_currency(self):
        await self.case_test("?from=TEST_RUB&to=None&amount=1", 400, {"error": "TO currency not found"})

    async def test_convert_when_amount_lower_0(self):
        await self.case_test("?from=TEST_RUB&to=USD&amount=-10", 400, [{
            "loc": [
                "amount"
            ],
            "msg": "ensure this value is greater than or equal to 0",
            "type": "value_error.number.not_ge",
            "ctx": {
                "limit_value": 0
            },
            "in": "query string"
        }])

    async def test_convert_when_params_correct(self):
        amount = 10
        await self.case_test("?from=FIXED_RUB&to=USD&amount=" + str(amount), 200, {"value": 60 * amount})
