from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4, UUID

from .elasticsearch import ElasticsearchClient
from .meilisearch import MeilisearchClient
from .base import SearchClient
from schemas import Movie, MovieUpdate, Filters
from app_vars import ENGINE_TO_USE


async def create_index():
    es_client = ElasticsearchClient()
    ms_client = MeilisearchClient()

    await es_client.create_index()
    await ms_client.create_index()


async def close_connections():
    es_client = ElasticsearchClient()
    await es_client.close()


def get_client() -> SearchClient:
    engine = ENGINE_TO_USE.lower()
    if engine.startswith("elastic"):
        return ElasticsearchClient
    elif engine.startswith("meili"):
        return MeilisearchClient
    else:
        raise HTTPException(status_code=400, detail="Search Engine Not Configured")


async def insert(payload: Movie) -> dict:
    es_client = ElasticsearchClient()
    ms_client = MeilisearchClient()

    insertion_data = payload.model_dump()
    time = datetime.now()
    insertion_data.update({
        "id": str(uuid4()),
        "created_at": time.isoformat(),
        "updated_at": time.isoformat()
    })

    await es_client.insert(data=insertion_data)
    await ms_client.insert(data=insertion_data)

    return insertion_data


async def get(movie_id: UUID) -> dict:
    client = get_client()()
    return await client.get(document_id=movie_id)


async def update(movie_id: UUID, payload: MovieUpdate) -> dict:
    es_client = ElasticsearchClient()
    ms_client = MeilisearchClient()

    update_data = payload.model_dump(exclude_unset=True)
    update_data.update({"updated_at": datetime.now().isoformat()})

    await es_client.update(document_id=movie_id, data=update_data)
    await ms_client.update(document_id=movie_id, data=update_data)

    return await get(movie_id=movie_id)


async def get_all(filters: Filters) -> dict:
    client = get_client()()
    return await client.get_all(filters=filters)


async def delete(movie_id: UUID):
    es_client = ElasticsearchClient()
    ms_client = MeilisearchClient()

    await es_client.delete(document_id=movie_id)
    await ms_client.delete(document_id=movie_id)


async def list_directors() -> list:
    client = get_client()()
    return await client.get_all_directors()
