import json
import logging
from datetime import datetime
from typing import Callable, List, Optional

from saleor_algolia.algolia.client import Algolia
from saleor_algolia.configuration import schemas
from saleor_algolia.saleor_gql import get_channels, get_saleor_client
from saleor_algolia.transformation.utils import get_transformator

logger = logging.getLogger(__name__)


async def fetch_channels(session):
    response = await session.execute(get_channels())
    return [channel["slug"] for channel in response["channels"]]


async def index_products_task(
    saleor_domain: str,
    product_ids: List[str],
    webhook: schemas.ActiveWebhook,
    config: schemas.ConfigurationData,
    after: Optional[str] = None,
    loop_callback: Optional[Callable] = None,
) -> None:
    """Task for indexing product."""
    logger.info("Task Index Product: Started")

    algolia = Algolia(app_id=config.algolia_app_id, api_key=config.algolia_api_key)
    total_indexed = 0
    transformator = get_transformator(webhook.transformation_type, config)
    get_products_query = await transformator.get_products_query()
    async with get_saleor_client(saleor_domain, config._auth_token) as session:
        channel_slugs = set(await fetch_channels(session))
        for language_slug in config.languages_list:
            has_next_page = True
            start_datetime = datetime.now()
            while has_next_page:
                logger.debug("Pulling data from Saleor")
                response = await session.execute(
                    get_products_query,
                    variable_values={
                        "first": 100,
                        "product_ids": product_ids,
                        "language": language_slug,
                        "after": after,
                    },
                )
                has_next_page = response["products"]["pageInfo"]["hasNextPage"]

                logger.debug("Transforming data")
                transformed_data = [
                    {
                        "action": record["action"],
                        "indexName": algolia.get_index_name(
                            language_slug, record["channel_slug"]
                        ),
                        "body": record["body"],
                    }
                    async for record in transformator(
                        response["products"]["edges"], channel_slugs
                    )
                ]

                logger.debug("Indexing in Algolia")
                algolia_response = await algolia.batch_operation(transformed_data)

                indexed = len(response["products"]["edges"])
                total_indexed += indexed
                end_datetime = datetime.now()
                datetime_delta = end_datetime - start_datetime
                logger.info(
                    "Indexed %s (from: %s, to %s), total: %s, took: %s",
                    indexed,
                    after,
                    response["products"]["pageInfo"]["endCursor"],
                    total_indexed,
                    datetime_delta,
                )
                if loop_callback:
                    loop_callback(
                        indexed=indexed,
                        start_cursor=after,
                        end_cursor=response["products"]["pageInfo"]["endCursor"],
                        total_indexed=total_indexed,
                        datetime_delta=datetime_delta,
                    )
                after = response["products"]["pageInfo"]["endCursor"]

    algolia_response.wait()
    logger.info(
        "Task Index Product: Successfully ended, algolis tasks: %s",
        json.dumps(algolia_response.raw_response["taskID"]),
    )


async def delete_products_task(
    saleor_domain: str,
    product_ids: List[str],
    webhook: schemas.ActiveWebhook,
    config: schemas.ConfigurationData,
) -> None:
    """Task for deleting product."""
    logger.info("Task Delete Product: Started")

    algolia = Algolia(app_id=config.algolia_app_id, api_key=config.algolia_api_key)

    async with get_saleor_client(saleor_domain, config._auth_token) as session:
        channel_slugs = set(await fetch_channels(session))

    for language_slug in config.languages_list:
        operations = []
        for channel_slug in channel_slugs:
            operations.extend(
                [
                    {
                        "action": "deleteObject",
                        "indexName": algolia.get_index_name(
                            language_slug, channel_slug
                        ),
                        "body": {"objectID": product_id},
                    }
                    for product_id in product_ids
                ]
            )
        await algolia.batch_operation(records=operations)

    logger.info("Task Delete Product: Successfully ended")
