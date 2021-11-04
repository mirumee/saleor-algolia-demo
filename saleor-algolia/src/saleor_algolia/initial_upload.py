import logging
import logging.config
from asyncio.exceptions import TimeoutError

from tqdm import tqdm

from saleor_algolia.configuration import models, schemas
from saleor_algolia.db.conn import DBSession
from saleor_algolia.products.tasks import index_products_task
from saleor_algolia.saleor_gql import get_saleor_client, get_total_products
from saleor_algolia.settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

after = None


async def get_total_from_saleor(saleor_domain, config, after=None):
    async with get_saleor_client(saleor_domain, config._auth_token) as session:
        response = await session.execute(
            get_total_products(), variable_values={"after": after}
        )
        return response["products"]["totalCount"]


def state_wrapper(state):
    def wrapped(func):
        def inner(*args, **kwargs):
            return func(state, *args, **kwargs)

        return inner

    return wrapped


def loop_callback(
    state, indexed, start_cursor, end_cursor, total_indexed, datetime_delta
):
    if pbar := state["pbar"]:
        pbar.update(indexed)
    state["last_end_cursor"] = end_cursor


async def run_index_products_task(saleor_domain, product_ids, after=None):
    with DBSession() as db:
        config = schemas.ConfigurationData.from_orm(
            await models.Configuration.get_domain_config(db, saleor_domain)
        )

    state = {"pbar": None, "last_end_cursor": after}

    if not product_ids:
        total = await get_total_from_saleor(saleor_domain, config=config, after=after)
        logger.info("Indexing a total of %s products", total)
        state["pbar"] = tqdm(total=total)
        callback = state_wrapper(state)(loop_callback)

    webhook = config.get_active_webhook_by_type(schemas.WebhookType.PRODUCT_UPDATED)

    while True:
        try:
            await index_products_task(
                saleor_domain,
                product_ids,
                webhook,
                config,
                after=state["last_end_cursor"],
                loop_callback=callback,
            )
            break
        except TimeoutError:
            print(
                f"Timeout when trying from {state['last_end_cursor']}, trying again..."
            )
            continue

    if pbar := state["pbar"]:
        pbar.close()
