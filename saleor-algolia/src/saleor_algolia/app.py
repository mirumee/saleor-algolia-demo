import logging

import sentry_sdk
from fastapi import Request
from fastapi.responses import JSONResponse
from saleor_app.app import SaleorApp
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from saleor_algolia import VERSION
from saleor_algolia.app_config import (
    get_webhook_details,
    store_app_data,
    validate_domain,
)
from saleor_algolia.configuration.endpoints import router as configuration_router
from saleor_algolia.healthcheck.endpoints import router as healthcheck_router
from saleor_algolia.products.endpoints import router as products_router
from saleor_algolia.settings import settings
from saleor_algolia.webhooks import webhook_handlers

LOGGER = logging.getLogger(__name__)


app = SaleorApp(
    validate_domain=validate_domain,
    save_app_data=store_app_data,
    webhook_handlers=webhook_handlers,
    get_webhook_details=get_webhook_details,
)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=VERSION,
    )
    app = SentryAsgiMiddleware(app).app


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "type": exc.__class__.__name__,
            "message": str(exc),
        },
    )


app.configuration_router.include_router(configuration_router)
app.include_router(products_router)
app.include_router(healthcheck_router)

app.include_saleor_app_routes()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_headers=settings.cors_allow_headers,
    allow_methods=settings.cors_allow_methods,
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
