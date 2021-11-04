import logging

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from saleor_app.schemas.handlers import Payload

from saleor_algolia.configuration import models, schemas
from saleor_algolia.db import DBSession
from saleor_algolia.products.tasks import delete_products_task, index_products_task

logger = logging.getLogger(__name__)


def webhook_controler(webhook_type: str):
    def inner(func):
        async def wrapper(payload: Payload, saleor_domain: str):
            logger.debug("Received webhook: %s", payload)
            with DBSession() as db:
                config = schemas.ConfigurationData.from_orm(
                    await models.Configuration.get_domain_config(db, saleor_domain)
                )
            if not config.algolia_app_id or not config.algolia_api_key:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": "Algolia configuration missing for domain",
                        "data": {},
                    },
                )
            if webhook := config.get_active_webhook_by_type(webhook_type):
                return await func(payload, saleor_domain, webhook, config)
            else:
                logger.info("%s webhook type is disabled in config", webhook_type)
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Webhook disabled",
                        "data": {},
                    },
                )

        return wrapper

    return inner


async def reindex_product(
    payload: Payload,
    saleor_domain: str,
    webhook: schemas.ActiveWebhook,
    config: schemas.ConfigurationData,
):
    tasks = BackgroundTasks()
    tasks.add_task(
        index_products_task,
        saleor_domain=saleor_domain,
        product_ids=[product["id"] for product in payload],
        webhook=webhook,
        config=config,
    )
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "message": "Reindexing new product in the background.",
            "data": {},
        },
        background=tasks,
    )


async def reindex_product_variant_change(
    payload: Payload,
    saleor_domain: str,
    webhook: schemas.ActiveWebhook,
    config: schemas.ConfigurationData,
):
    tasks = BackgroundTasks()
    tasks.add_task(
        index_products_task,
        saleor_domain=saleor_domain,
        product_ids=[variant["product_id"] for variant in payload],
        webhook=webhook,
        config=config,
    )
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "message": "Reindexing new product in the background.",
            "data": {},
        },
        background=tasks,
    )


async def delete_product_from_index(
    payload: Payload,
    saleor_domain: str,
    webhook: schemas.ActiveWebhook,
    config: schemas.ConfigurationData,
):

    tasks = BackgroundTasks()
    tasks.add_task(
        delete_products_task,
        saleor_domain=saleor_domain,
        product_ids=[product["id"] for product in payload],
        webhook=webhook,
        config=config,
    )
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "message": "Removing product in the background.",
            "data": {},
        },
        background=tasks,
    )


product_created = webhook_controler(schemas.WebhookType.PRODUCT_CREATED)(
    reindex_product
)
product_updated = webhook_controler(schemas.WebhookType.PRODUCT_UPDATED)(
    reindex_product
)
product_deleted = webhook_controler(schemas.WebhookType.PRODUCT_DELETED)(
    delete_product_from_index
)
product_variant_created = webhook_controler(
    schemas.WebhookType.PRODUCT_VARIANT_CREATED
)(reindex_product_variant_change)
product_variant_updated = webhook_controler(
    schemas.WebhookType.PRODUCT_VARIANT_UPDATED
)(reindex_product_variant_change)
product_variant_deleted = webhook_controler(
    schemas.WebhookType.PRODUCT_VARIANT_DELETED
)(reindex_product_variant_change)
