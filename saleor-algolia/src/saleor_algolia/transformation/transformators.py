from abc import ABC, abstractmethod
from typing import Set

from saleor_algolia.saleor_gql import get_products_query as saleor_get_products_query
from saleor_algolia.transformation.client import TransformClient
from saleor_algolia.transformation.schemas import AlgoliaProduct


class Transformator(ABC):
    @abstractmethod
    async def __call__(self, payload):
        raise NotImplementedError

    @abstractmethod
    async def get_products_query(self):
        raise NotImplementedError


class LocalTransformator(Transformator):
    async def get_products_query(self):
        return saleor_get_products_query()

    async def __call__(self, payload, channel_slugs: Set[str]):
        for record in payload:
            for channel_slug in channel_slugs:
                product = AlgoliaProduct.from_saleor_product(record["node"]).dict()

                if channel_slug in product["channels"]:
                    product_channel_data = product.pop("channels")
                    channel_listing = product_channel_data[channel_slug]
                    product["isAvailableForPurchase"] = channel_listing[
                        "isAvailableForPurchase"
                    ]
                    product["isPublished"] = channel_listing["isPublished"]
                    product["minPrice"] = channel_listing["minPrice"]
                    product["maxPrice"] = channel_listing["maxPrice"]
                    product["currency"] = channel_listing["currency"]
                    yield {
                        "action": "updateObject",
                        "channel_slug": channel_slug,
                        "body": product,
                    }
                else:
                    yield {
                        "action": "deleteObject",
                        "channel_slug": channel_slug,
                        "body": {"objectID": product["objectID"]},
                    }

        return


class RemoteTransformator(Transformator):
    def __init__(self, url, api_key):
        self.client = TransformClient(url=url, api_key=api_key)

    async def get_products_query(self):
        response = await self.client.get_product_fragment()
        return saleor_get_products_query(response)

    async def __call__(self, payload, channel_slugs: Set[str]):
        response = await self.client.transform(payload, list(channel_slugs))
        for record in response:
            yield record
        return
