from urllib.parse import urlparse

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from saleor_algolia.configuration.schemas import TransformationType
from saleor_algolia.db.conn import Base


class ActiveWebhook(Base):
    __tablename__ = "configuration_activewebhooks"

    configuration_id = Column(
        Integer, ForeignKey("configurations.id"), primary_key=True
    )
    configuration_webhook_id = Column(
        Integer, ForeignKey("configuration_webhooks.id"), primary_key=True
    )
    transformation_type = Column(Enum(TransformationType), default=False)
    configuration = relationship("Configuration", back_populates="active_webhooks")
    webhook = relationship("Webhook")


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    saleor_domain = Column(String(255), nullable=True, unique=True)
    auth_token = Column(String(255), nullable=True)
    webhook_id = Column(String(255), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    algolia_app_id = Column(String(255), nullable=True)
    algolia_api_key = Column(String(255), nullable=True)
    languages_list = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=False)
    transformation_service_url = Column(Text(), nullable=True)
    transformation_service_api_key = Column(Text(), nullable=True)
    active_webhooks = relationship(
        "ActiveWebhook", back_populates="configuration", cascade="all, delete-orphan"
    )

    @classmethod
    async def get_domain_config(cls, db, saleor_domain: str):
        if saleor_domain.startswith("http"):
            saleor_domain = urlparse(saleor_domain).netloc

        return (
            db.query(cls)
            .outerjoin(cls.active_webhooks)
            .filter(
                Configuration.saleor_domain == saleor_domain,
                Configuration.is_active
                == True,  # noqa: E712 _in does not work for all databases
            )
            .first()
        )


class Webhook(Base):
    __tablename__ = "configuration_webhooks"

    id = Column(Integer, primary_key=True)
    type = Column(String(255), nullable=True)
