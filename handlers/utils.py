from typing import Optional

from aiohttp import web


def get_error_response(text: str, status: Optional[int] = 400):
    return web.json_response({'error': text}, status=status)
