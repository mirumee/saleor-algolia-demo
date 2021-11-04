import logging
from typing import Any, List
from urllib.parse import urljoin

import aiohttp
import orjson
from aiohttp.client_exceptions import ClientResponseError

LOGGER = logging.getLogger(__name__)


class TransformClient:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def get_headers(self):
        headers = {
            "Content-Encoding": "gzip",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def get_product_fragment(self):
        async with aiohttp.ClientSession(raise_for_status=False) as session:
            async with session.get(
                urljoin(self.url, "product_fragment"),
                headers=self.get_headers(),
            ) as response:
                response_data = await response.text()
            try:
                response.raise_for_status()
            except ClientResponseError as error:
                LOGGER.error(
                    "Failed to fetch query product fragment from %s",
                    error.request_info.url,
                )
                raise
            return response_data

    async def transform(self, records: List[Any], channel_slugs: List[str]):
        request_data = {"context": {"channel_slugs": channel_slugs}, "records": records}
        async with aiohttp.ClientSession(raise_for_status=False) as session:
            async with session.post(
                urljoin(self.url, "transform"),
                data=orjson.dumps(request_data),
                headers=self.get_headers(),
            ) as response:
                response_data = await response.json()
            try:
                response.raise_for_status()
            except ClientResponseError as error:
                LOGGER.error(
                    "Failed to transform records with %s", error.request_info.url
                )
                LOGGER.debug(orjson.dumps(response_data))
                raise
            return response_data
