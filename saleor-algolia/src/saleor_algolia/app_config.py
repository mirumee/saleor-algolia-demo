import logging

from saleor_app.schemas.core import DomainName, WebhookData

from saleor_algolia.configuration.exceptions import ConfigurationMissing
from saleor_algolia.configuration.models import Configuration
from saleor_algolia.db import DBSession

LOGGER = logging.getLogger(__name__)


async def validate_domain(domain_name: str) -> bool:
    LOGGER.debug("validating domain %s", domain_name)

    with DBSession() as db:
        db_config = await Configuration.get_domain_config(db, domain_name)

    if db_config:
        return True

    return False


async def store_app_data(domain_name: DomainName, app_data: WebhookData):
    LOGGER.debug("storing app data %s", domain_name)
    with DBSession() as db:
        config = await Configuration.get_domain_config(db, domain_name)
        if not config:
            raise ConfigurationMissing("Configuration missing")
        config.saleor_domain = domain_name
        config.auth_token = app_data.token
        config.webhook_id = app_data.webhook_id
        config.webhook_secret = app_data.webhook_secret_key
        db.commit()


async def get_webhook_details(domain_name: DomainName):
    with DBSession() as db:
        config = await Configuration.get_domain_config(db, domain_name)
        if not config:
            raise ConfigurationMissing("Configuration missing")
    return WebhookData(
        token=config.auth_token,
        webhook_id=config.webhook_id,
        webhook_secret_key=config.webhook_secret,
    )
