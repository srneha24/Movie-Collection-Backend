from elasticsearch import AsyncElasticsearch

from app_vars import ELASTICSEARCH_API_KEY, ELASTICSEARCH_HOST, INDEX_NAME
from .base import SearchClient


class ElasticsearchClient(SearchClient):
    client: AsyncElasticsearch
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ElasticsearchClient, cls).__new__(cls)
            cls._instance.client = AsyncElasticsearch(ELASTICSEARCH_HOST, api_key=ELASTICSEARCH_API_KEY)
        return cls._instance
    
    async def create_index(self):
        if not await self.client.indices.exists(index=INDEX_NAME):
            resp = await self.client.indices.create(index=INDEX_NAME)
            print(resp)

            await self.client.indices.put_mapping(
                index=INDEX_NAME,
                properties={
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "poster_url": {
                        "type": "keyword",
                        "index": False
                    },
                    "synopsis": {
                        "type": "text"
                    },
                    "director": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "review": {
                        "type": "text"
                    },
                    "rating": {
                        "type": "float"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "updated_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            )

    
    async def insert(self, data):
        document_id = data["id"]
        document = data.copy()
        document.pop("id")
        resp = await self.client.index(index=INDEX_NAME, id=document_id, document=document)
        print(resp)
    
    async def update(self, document_id, data):
        resp = await self.client.update(index=INDEX_NAME, id=str(document_id), doc=data)
        print(resp)
    
    async def get(self, document_id) -> dict:
        result = await self.client.get(index=INDEX_NAME, id=str(document_id))
        data = result["_source"]
        data.update({"id": result["_id"]})
        return data
    
    async def get_all(self, filters) -> dict:
        must = []
        conditions = dict()
        conditional_args = {
            "from": (filters.page - 1) * filters.limit,
            "size": filters.limit,
            "track_total_hits": True
        }

        if filters.search:
            conditions["should"] = [
                {
                    "multi_match": {
                        "query": filters.search,
                        "fields": [
                            "title^3",
                            "synopsis^2",
                            "review",
                            "director"
                        ]
                    }
                }
            ]
        
        if filters.rating:
            must.append({
                "range": {
                    "rating": {
                        "gt": float(filters.rating - 1),
                        "lte": float(filters.rating)
                    }
                }
            })
        
        if filters.release_year:
            must.append({
                "range": {
                    "release_date": {
                        "gte": f"{filters.release_year}-01-01",
                        "lte": f"{filters.release_year}-12-31",
                        "format": "yyyy-MM-dd"
                    }
                }
            })
        
        if filters.director:
            must.append({
                "term": {
                    "director": filters.director
                }
            })
        
        if must:
            conditions["must"] = must
        
        if conditions:
            conditional_args.update({
                "query": {
                    "bool": conditions
                }
            })
        else:
            conditional_args.update({
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "created_at": {
                            "order": "desc"
                        }
                    }
                ]
            })
        
        results = await self.client.search(index=INDEX_NAME, **conditional_args)
        data = []
        for hit in results['hits']['hits']:
            temp = {"id": hit["_id"]}
            temp.update(hit["_source"])
            data.append(temp)
        
        return {
            "data": data,
            "total_count": results["hits"]["total"]["value"]
        }
    
    async def delete(self, document_id):
        await self.client.delete(index=INDEX_NAME, id=str(document_id))
    
    async def get_all_directors(self) -> list:
        result = await self.client.search(
            index=INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "unique_directors": {
                        "terms": {
                            "field": "director.keyword",
                            "size": 1000,
                            "order": { "_key": "asc" }
                        }
                    }
                }
            }
        )

        unique_directors = [bucket["key"] for bucket in result["aggregations"]["unique_directors"]["buckets"]]
        return unique_directors
    
    async def close(self):
        await self.client.close()
