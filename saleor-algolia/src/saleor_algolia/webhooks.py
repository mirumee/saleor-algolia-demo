from saleor_app.schemas.handlers import WebhookHandlers

from saleor_algolia.products.webhooks import (
    product_created,
    product_deleted,
    product_updated,
    product_variant_created,
    product_variant_deleted,
    product_variant_updated,
)

webhook_handlers = WebhookHandlers(
    product_created=product_created,
    product_updated=product_updated,
    product_deleted=product_deleted,
    product_variant_created=product_variant_created,
    product_variant_updated=product_variant_updated,
    product_variant_deleted=product_variant_deleted,
)
