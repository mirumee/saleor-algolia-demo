from typing import Any, Dict, List, Union

from algoliasearch.search_client import SearchClient

from saleor_algolia.settings import settings


class Algolia:
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key
        self.client = SearchClient.create(app_id=self.app_id, api_key=self.api_key)

    def get_index_name(self, language_slug: str, channel_slug: str):
        return f"{settings.index_env}.products.{language_slug}.{channel_slug}"

    async def update_index(self, data: List[Dict[str, Any]], index: str):
        """
        Update Algolia's index. If a product is marked as visible in the channel listing,
        it will be saved into the index. If it's unmarked it will not be added or will be
        deleted if was added previously.
        """
        index = self.client.init_index(index)
        return index.save_objects(data)

    async def delete_by_id_from_index(
        self, algolia_object_ids: List[str], index: str
    ) -> None:
        """
        Remove products from index, by product ID.
        """
        index = self.client.init_index(index)
        return index.delete_objects(algolia_object_ids)

    async def batch_operation(self, records: List[Dict[str, Union[str, Any]]]):
        return self.client.multiple_batch(records)
