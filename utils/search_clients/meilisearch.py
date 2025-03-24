from meilisearch import Client
from meilisearch.index import Index
from meilisearch.errors import MeilisearchApiError
from datetime import datetime

from app_vars import MEILISEARCH_HOST, MEILISEARCH_API_KEY, INDEX_NAME
from .base import SearchClient


class MeilisearchClient(SearchClient):
    client: Client
    index: Index
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MeilisearchClient, cls).__new__(cls)
            cls._instance.client = Client(url=MEILISEARCH_HOST, api_key=MEILISEARCH_API_KEY)
        return cls._instance

    async def create_index(self):
        try:
            self.index = self.client.get_index(INDEX_NAME)
        except MeilisearchApiError as e:
            if e.code == "index_not_found":
                resp = self.client.create_index(INDEX_NAME, {"primaryKey": "id"})
                res = self.client.wait_for_task(resp.task_uid)
                print(res)

                self.index = self.client.get_index(INDEX_NAME)
                self.index.update_settings(
                    {
                        "searchableAttributes": [
                            "title",
                            "synopsis",
                            "director",
                            "review"
                        ],
                        "sortableAttributes": [
                            "title",
                            "director",
                            "release_date",
                            "created_at",
                            "updated_at",
                            "rating"
                        ],
                        "filterableAttributes": [
                            "release_date",
                            "rating",
                            "created_at",
                            "updated_at",
                            "director"
                        ]
                    }
                )
            else:
                raise e
    
    async def insert(self, data):
        resp = self.index.add_documents(documents=[data])
        res = self.client.wait_for_task(resp.task_uid)
        print(res)
    
    async def update(self, document_id, data):
        data.update({"id": str(document_id)})
        resp = self.index.update_documents(documents=[data])
        res = self.client.wait_for_task(resp.task_uid)
        print(res)
    
    async def get(self, document_id) -> dict:
        return dict(self.index.get_document(document_id=str(document_id))).get("_Document__doc")
    
    async def get_all(self, filters) -> dict:
        conditional_args = {
            "opt_params": {
                "page": filters.page,
                "hitsPerPage": filters.limit
            }
        }
        conditions = []

        if filters.search:
            conditional_args["query"] = filters.search
        else:
            conditional_args["query"] = ""

        if filters.director:
            conditions.append(f'director = "{filters.director}"')
        
        if filters.rating:
            conditions.append(f'(rating > {(filters.rating - 1)} AND rating <= {filters.rating})')

        if filters.release_year:
            start_time = datetime.fromisoformat(f"{filters.release_year}-01-01 00:00:00").timestamp() * 1000
            end_time = datetime.fromisoformat(f"{filters.release_year}-12-31 23:59:59").timestamp() * 1000
            conditions.append(f'(release_date >= {start_time} AND release_date <= {end_time})')

        if not conditions:
            conditional_args["opt_params"]["sort"] = ["created_at:desc"]
        else:
            conditional_args["opt_params"]["filter"] = " AND ".join(conditions)
        
        results = self.index.search(**conditional_args)
        return {
            "data": results["hits"],
            "total_count": results["totalHits"]
        }

    async def delete(self, document_id):
        resp = self.index.delete_document(document_id=str(document_id))
        res = self.client.wait_for_task(resp.task_uid)
        print(res)
    
    async def get_all_directors(self) -> list:
        result = self.index.facet_search("director", "", {"sort": "asc"})
        unique_directors = [res["value"] for res in result["facetHits"]]
        return unique_directors
