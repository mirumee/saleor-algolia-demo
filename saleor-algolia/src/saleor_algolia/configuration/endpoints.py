import json
import logging

from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from saleor_app.deps import ConfigurationDataDeps, ConfigurationFormDeps
from sqlalchemy.orm import Session

from saleor_algolia.configuration import models, schemas
from saleor_algolia.db import get_db
from saleor_algolia.saleor_gql import get_languages, get_saleor_client
from saleor_algolia.settings import settings

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="configuration-form")
async def get_public_form(
    commons: ConfigurationFormDeps = Depends(),
):
    context = {
        "request": commons.request,
        "form_url": commons.request.url,
        "domain": commons.saleor_domain,
        "webhooks_values": [webhook.value for webhook in schemas.WebhookType],
    }

    async with get_saleor_client(commons.saleor_domain) as session:
        result = await session.execute(get_languages())
        context.update(
            languages=json.dumps(result["shop"]["languages"]),
        )
    return Jinja2Templates(directory=settings.templates_dir).TemplateResponse(
        "config.html", context
    )


@router.get(
    "/data", name="configuration-data", response_model=schemas.ConfigurationData
)
async def get_configuration_data(
    commons: ConfigurationDataDeps = Depends(), db: Session = Depends(get_db)
):
    db_config = await models.Configuration.get_domain_config(db, commons.saleor_domain)
    return schemas.ConfigurationData.from_orm(db_config)


@router.post(
    "/data", name="configuration-data-update", response_model=schemas.ConfigurationData
)
async def update_configuration_data(
    config_data: schemas.ConfigurationData,
    commons: ConfigurationDataDeps = Depends(),
    db: Session = Depends(get_db),
):
    db_config = await models.Configuration.get_domain_config(db, commons.saleor_domain)

    if config_data.algolia_app_id:
        db_config.algolia_app_id = config_data.algolia_app_id
    if config_data.algolia_api_key:
        db_config.algolia_api_key = config_data.algolia_api_key
    db_config.languages_list = ",".join(config_data.languages_list)
    if config_data.transformation_service:
        db_config.transformation_service_url = config_data.transformation_service.url
        db_config.transformation_service_api_key = (
            config_data.transformation_service.api_key
        )

    db_config.active_webhooks = []

    db_webhooks = {
        db_webhook.type: db_webhook
        for db_webhook in db.query(models.Webhook).filter(
            models.Webhook.type.in_(
                [active_webhook.type for active_webhook in config_data.active_webhooks]
            )
        )
    }

    for active_webhook in config_data.active_webhooks:
        db_active_webhook = models.ActiveWebhook(
            transformation_type=active_webhook.transformation_type,
        )
        db_active_webhook.webhook = db_webhooks[active_webhook.type]
        db_config.active_webhooks.append(db_active_webhook)
    db.commit()
    db.refresh(db_config)
    return db_config
