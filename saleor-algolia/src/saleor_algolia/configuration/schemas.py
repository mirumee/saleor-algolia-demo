from enum import Enum
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, PrivateAttr, validator


class TransformationType(str, Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"


class WebhookType(str, Enum):
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_UPDATED = "PRODUCT_UPDATED"
    PRODUCT_DELETED = "PRODUCT_DELETED"
    PRODUCT_VARIANT_CREATED = "PRODUCT_VARIANT_CREATED"
    PRODUCT_VARIANT_UPDATED = "PRODUCT_VARIANT_UPDATED"
    PRODUCT_VARIANT_DELETED = "PRODUCT_VARIANT_DELETED"


class ActiveWebhook(BaseModel):
    type: WebhookType
    transformation_type: TransformationType

    class Config:
        orm_mode = True


class TransformationService(BaseModel):
    url: Optional[AnyUrl]
    api_key: Optional[str]

    class Config:
        orm_mode = True


class ConfigurationData(BaseModel):
    _id: int = PrivateAttr()
    _auth_token: str = PrivateAttr()
    algolia_app_id: Optional[str]
    algolia_api_key: Optional[str]
    languages_list: List[str]
    active_webhooks: List[ActiveWebhook]
    transformation_service: Optional[TransformationService]

    def get_active_webhook_by_type(self, _type):
        for active_webhook in self.active_webhooks:
            if active_webhook.type == _type:
                return active_webhook
        return None

    @classmethod
    def from_orm(cls, obj):
        data = {
            "algolia_app_id": obj.algolia_app_id,
            "algolia_api_key": obj.algolia_api_key,
            "languages_list": [],
            "active_webhooks": [],
        }
        if obj.languages_list:
            data["languages_list"] = list(set(obj.languages_list.split(",")))

        transformation_service_data = {}
        if obj.transformation_service_url:
            transformation_service_data["url"] = obj.transformation_service_url
        if obj.transformation_service_api_key:
            transformation_service_data["api_key"] = obj.transformation_service_api_key
        if transformation_service_data:
            data["transformation_service"] = transformation_service_data

        data["active_webhooks"] = [
            {
                "transformation_type": entry.transformation_type,
                "type": entry.webhook.type,
            }
            for entry in obj.active_webhooks
        ]
        instance = cls.parse_obj(data)
        instance._auth_token = obj.auth_token
        return instance

    @validator("transformation_service")
    def check_transformation_service(cls, value, values):
        if (
            any(
                (
                    active_webhook.transformation_type == TransformationType.REMOTE
                    for active_webhook in values.get("active_webhooks", [])
                )
            )
            and not value
        ):
            raise ValueError(
                "Provide `transformation_service` to enable transformation"
            )
        return value

    class Config:
        orm_mode = True
