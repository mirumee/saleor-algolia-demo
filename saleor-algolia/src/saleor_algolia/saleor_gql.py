from asyncio.exceptions import TimeoutError

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from saleor_app.graphql import get_saleor_api_url

from saleor_algolia.products.queries import (
    FETCH_CHANNELS,
    FETCH_LANGUAGES,
    FETCH_PRODUCT_BY_ID_DATA,
    FETCH_PRODUCTS_DATA,
    FETCH_TOTAL_PRODUCTS,
    PRODUCT_DATA_FRAGMENT,
)


class RetryAIOHTTPTransport(AIOHTTPTransport):
    def __init__(self, retries=3, *args, **kwargs):
        self.retries = retries
        super().__init__(*args, **kwargs)

    async def execute(self, *args, **kwargs):
        attempts = 1
        while True:
            try:
                return await super().execute(*args, **kwargs)
            except TimeoutError:
                if attempts < self.retries:
                    attempts += 1
                    continue
                raise


def get_saleor_client(saleor_domain, token=None):
    transport_kwargs = {
        "url": get_saleor_api_url(saleor_domain),
        "timeout": 1,
        "retries": 3,
    }
    if token is not None:
        transport_kwargs["headers"] = {"Authorization": f"Bearer {token}"}
    return Client(
        transport=RetryAIOHTTPTransport(**transport_kwargs),
        fetch_schema_from_transport=False,
    )


def get_products_query(fragment=PRODUCT_DATA_FRAGMENT):
    return gql(FETCH_PRODUCTS_DATA % fragment)


def get_product_by_id_query():
    return gql(FETCH_PRODUCT_BY_ID_DATA)


def get_languages():
    return gql(FETCH_LANGUAGES)


def get_channels():
    return gql(FETCH_CHANNELS)


def get_total_products():
    return gql(FETCH_TOTAL_PRODUCTS)
