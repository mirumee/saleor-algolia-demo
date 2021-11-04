from saleor_algolia.configuration import schemas
from saleor_algolia.transformation.exceptions import UnknownTransformator
from saleor_algolia.transformation.transformators import (
    LocalTransformator,
    RemoteTransformator,
)


def get_transformator(type: str, config: schemas.ConfigurationData):
    if type == schemas.TransformationType.LOCAL:
        return LocalTransformator()
    elif type == schemas.TransformationType.REMOTE:
        return RemoteTransformator(
            url=config.transformation_service.url,
            api_key=config.transformation_service.api_key,
        )
    else:
        raise UnknownTransformator(f"Transformator of type {type} is not supported")
