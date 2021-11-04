from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from saleor_app.deps import require_permission, saleor_domain_header
from saleor_app.schemas.core import SaleorPermissions

from saleor_algolia.configuration import models, schemas
from saleor_algolia.db.conn import get_db
from saleor_algolia.products.tasks import index_products_task

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", name="index-task")
async def index_view(
    request: Request,
    _permissions=Depends(require_permission([SaleorPermissions.MANAGE_PRODUCTS])),
    saleor_domain=Depends(saleor_domain_header),
    db=Depends(get_db),
) -> JSONResponse:
    """After POST request will run index all products task in the background."""
    config = schemas.ConfigurationData.from_orm(
        await models.Configuration.get_domain_config(db, saleor_domain)
    )
    webhook = config.get_active_webhook_by_type(schemas.WebhookType.PRODUCT_CREATED)

    tasks = BackgroundTasks()
    tasks.add_task(
        index_products_task,
        saleor_domain=saleor_domain,
        product_ids=[],
        webhook=webhook,
        config=config,
    )
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "message": "Reindexing all products in the background.",
            "data": {},
        },
        background=tasks,
    )
