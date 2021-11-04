import os
from pathlib import Path
from typing import List, Optional

from saleor_app.conf import Settings, SettingsManifest
from saleor_app.schemas.core import SaleorPermissions


class AppSettings(Settings):
    database_dsn: str
    index_env: str = "DEV"
    cors_allow_origins: List[str] = []
    cors_allow_headers: List[str] = []
    cors_allow_methods: List[str] = ["GET"]
    sentry_dsn: Optional[str]
    environment: str


PROJECT_DIR = Path(__file__).parent.absolute()

settings = AppSettings(
    app_name="Seleor Algolia",
    project_dir=PROJECT_DIR,
    static_dir=PROJECT_DIR / "static" / "static",
    templates_dir=PROJECT_DIR / "static",
    manifest=SettingsManifest(
        name="Seleor Algolia",
        version="1.0.0",
        about="Algolia search-as-a-service and full suite of APIs allow teams to easily develop tailored, fast Search and Discovery experiences that delight and convert.",
        data_privacy="",
        data_privacy_url="",
        id="saleor-algolia",
        permissions=[
            SaleorPermissions.MANAGE_PRODUCTS,
        ],
        homepage_url="https://github.com/mirumee/saleor-algolia",
        support_url="https://github.com/mirumee/saleor-algolia",
        app_url="https://github.com/mirumee/saleor-algolia",
        extensions=[],
        configuration_url_for="configuration-form",
    ),
    cors_allow_origins=["*"],
    cors_allow_headers=["*"],
    cors_allow_methods=["OPTIONS", "GET", "POST"],
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "healthcheck_filter": {
            "()": "saleor_algolia.healthcheck.log_filter.HealthCheckFilter"
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler"
            if settings.debug
            else "logging.StreamHandler",
            "filters": ["healthcheck_filter"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("ROOT_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "saleor_algolia": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "saleor_algolia.products.tasks": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "saleor_algolia.initial_upload": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "gql": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
    },
}
