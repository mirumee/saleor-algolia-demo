from typing import Any, Dict, List, Optional

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
    def _get_translated_name(obj):
        if translation := obj.get("translation"):
            return translation["name"] or obj["name"]
        return obj["name"]

    @classmethod
    def _get_category_names(cls, category):
        while category:
            yield cls._get_translated_name(category)
            category = category["parent"]

    @classmethod
    def _get_category_tree_list(cls, category_names):
        while category_names:
            yield " > ".join(
                reversed([category_name for category_name in category_names])
            )
            category_names.pop()

    @classmethod
    def _get_attributes(cls, attributes):
        for attr in attributes:
            if attr["values"] is None:
                continue
            values = []
            for value in attr["values"]:
                values.append(cls._get_translated_name(value))
            yield attr["attribute"]["slug"], values

    @classmethod
    def _get_collections(cls, collections):
        for collection in collections:
            yield {
                "name": cls._get_translated_name(collection),
                "slug": collection["slug"],
            }

    @classmethod
    def _get_channel_listings(cls, channel_listings):
        for channel in channel_listings:
            price_range = (channel.get("pricing") or {}).get("priceRange")
            if price_range is None:
                minPrice = ""
                maxPrice = ""
                currency = ""
            else:
                minPrice = price_range["start"]["gross"]["amount"]
                maxPrice = price_range["stop"]["gross"]["amount"]
                currency = price_range["start"]["gross"]["currency"]

            yield channel["channel"]["slug"], {
                "name": channel["channel"]["name"],
                "slug": channel["channel"]["slug"],
                "isAvailableForPurchase": channel["isAvailableForPurchase"],
                "isPublished": channel["isPublished"],
                "minPrice": minPrice,
                "maxPrice": maxPrice,
                "currency": currency,
            }

    @classmethod
    def saleor_product_to_algolia(cls, product: Dict[str, str]):
        data = {
            "objectID": product["id"],
            "id": product["id"],
            "name": cls._get_translated_name(product),
            "slug": product["slug"],
            "productType": product["productType"]["name"].lower(),
            "channels": {},
        }

        data["category"] = cls._get_category_tree_list(
            list(cls._get_category_names(product["category"]))
        )
        data["attributes"] = cls._get_attributes(product["attributes"])
        data["collections"] = cls._get_collections(product["collections"])

        data["channels"] = cls._get_channel_listings(product["channelListings"])

        if thumbnail := product.get("thumbnail"):
            data["thumbnail"] = thumbnail["url"]

        if product["weight"]:
            data["weight"] = product["weight"]

        return data

    @classmethod
    def from_saleor_product(cls, product: Dict[str, str]):
        return cls.parse_obj(cls.saleor_product_to_algolia(product))
