from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel


class Channel(BaseModel):
    name: str
    slug: str
    isAvailableForPurchase: bool
    isPublished: bool
    minPrice: str
    maxPrice: str
    currency: str


class AlgoliaProduct(BaseModel):
    objectID: str
    id: str
    name: str
    slug: str
    category: List[str]
    productType: str
    attributes: Dict[str, Any]
    collections: List[Dict[str, Any]]
    thumbnail: Optional[str]
    weight: Optional[Dict[str, Any]] = None
    channels: Dict[str, Channel]

    @staticmethod
    def get_translated_name(obj):
        if translation := obj.get("translation"):
            return translation["name"] or obj["name"]
        return obj["name"]

    @classmethod
    def saleor_product_to_algolia(cls, product: Dict[str, str]):
        data = {
            "objectID": product["id"],
            "id": product["id"],
            "name": cls.get_translated_name(product),
            "slug": product["slug"],
            "productType": product["productType"]["name"].lower(),
            "channels": {},
        }

        category_names = []
        category = product["category"]
        while category:
            category_names.append(cls.get_translated_name(category))
            category = category["parent"]

        category_names = category_names[::-1]
        category_tree_list = []
        while category_names:
            category_tree_list.append(" > ".join(category_names))
            category_names.pop()

        data["category"] = category_tree_list

        data["attributes"] = {}
        for attr in product["attributes"]:
            if attr["values"] is None:
                continue
            values = []
            for value in attr["values"]:
                values.append(cls.get_translated_name(value))
            data["attributes"][attr["attribute"]["slug"]] = values

        data["collections"] = []
        for collection in product["collections"]:
            data["collections"].append(
                {
                    "name": cls.get_translated_name(collection),
                    "slug": collection["slug"],
                }
            )

        for channel in product["channelListings"]:
            price_range = (channel.get("pricing") or {}).get("priceRange")
            if price_range is None:
                minPrice = ""
                maxPrice = ""
                currency = ""
            else:
                minPrice = price_range["start"]["gross"]["amount"]
                maxPrice = price_range["stop"]["gross"]["amount"]
                currency = price_range["start"]["gross"]["currency"]

            data["channels"][channel["channel"]["slug"]] = {
                "name": channel["channel"]["name"],
                "slug": channel["channel"]["slug"],
                "isAvailableForPurchase": channel["isAvailableForPurchase"],
                "isPublished": channel["isPublished"],
                "minPrice": minPrice,
                "maxPrice": maxPrice,
                "currency": currency,
            }

        if thumbnail := product.get("thumbnail"):
            data["thumbnail"] = thumbnail["url"]

        if product["weight"]:
            data["weight"] = product["weight"]

        return data

    @classmethod
    def from_saleor_product(cls, product: Dict[str, str]):
        return cls.parse_obj(cls.saleor_product_to_algolia(product))


class RecordContext(BaseModel):
    channel_slugs: List[str]


class TransformationRequest(BaseModel):
    context: RecordContext
    records: List[Any]


class AlgoliaOperation(BaseModel):
    action: str
    channel_slug: str
    body: Any


app = FastAPI()


@app.get("/product_fragment")
async def product_fragment():
    return PlainTextResponse(
        content=PRODUCT_DATA_FRAGMENT,
        status_code=200,
    )

@app.post("/transform", response_model=List[AlgoliaOperation])
async def transform(transformation_request: TransformationRequest):
    channel_slugs = transformation_request.context.channel_slugs

    operations = []

    for record in transformation_request.records:
        for channel_slug in channel_slugs:
            product = AlgoliaProduct.from_saleor_product(record["node"]).dict()

            if channel_slug in product["channels"]:
                product_channel_data = product.pop("channels")
                channel_listing = product_channel_data[channel_slug]
                product["isAvailableForPurchase"] = channel_listing[
                    "isAvailableForPurchase"
                ]
                product["isPublished"] = channel_listing["isPublished"]
                product["minPrice"] = channel_listing["minPrice"]
                product["maxPrice"] = channel_listing["maxPrice"]
                product["currency"] = channel_listing["currency"]
                operation = AlgoliaOperation(
                    action="updateObject",
                    channel_slug=channel_slug,
                    body=product,
                )
            else:
                operation = AlgoliaOperation(
                    action="deleteObject",
                    channel_slug=channel_slug,
                    body={"objectID": product["objectID"]},
                )
            operations.append(operation)

    return operations


PRODUCT_DATA_FRAGMENT = """
    id
    channelListings {
        id
        channel {
            name
            slug
        }
        isAvailableForPurchase
        isPublished
        pricing {
            onSale
            priceRange {
                start {
                    gross {
                        amount
                        currency
                    }
                }
                stop {
                    gross {
                        amount
                        currency
                    }
                }
            }
        }
    }
    translation(languageCode: $language) {
        name
    }
    slug
    name
    category {
        name
        translation(languageCode: $language) {
            name
        }
        parent {
            name
            translation(languageCode: $language) {
                name
            }
            parent {
                name
                translation(languageCode: $language) {
                    name
                }
                parent {
                    name
                    translation(languageCode: $language) {
                        name
                    }
                }
            }
        }
    }
    collections {
        id
        slug
        name
        backgroundImage {
            url
        }
        translation(languageCode: $language) {
            name
        }
    }
    thumbnail {
        url
        alt
    }
    weight {
        value
        unit
    }
    productType {
        name
    }
    attributes {
        attribute {
        name
        slug
        inputType
        translation(languageCode: $language) {
            name
        }
        }
        values {
        name
        translation(languageCode: $language){
            name
        }
        slug
        boolean
        date
        value
        }
    }
    variants {
        name
        translation(languageCode: $language) {
            name
        }
        quantityAvailable
        weight {
            value
            unit
        }
        attributes {
            attribute {
                name
                slug
                inputType
                translation(languageCode: $language) {
                    name
                }
            }
            values {
                name
                translation(languageCode: $language) {
                    name
                }
                slug
                boolean
                date
                value
            }
        }
    }
"""
