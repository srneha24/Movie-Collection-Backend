from fastapi import FastAPI, Request, Path, Depends, Response
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from uuid import UUID

from schemas import Movie, MovieUpdate, Filters, MovieResponse, APIResponse, APIResponsePaginated
from utils.search_clients import create_index, close_connections, insert, update, get, get_all, delete, list_directors
from utils.pagination import Pagination


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_index()
    yield
    await close_connections()


app = FastAPI(lifespan=lifespan)


@app.post("/movie")
async def add_movie(request: Request, payload: Movie):
    data = await insert(payload=payload)
    response = APIResponse(message="Movie Added", data=MovieResponse.model_validate(data))
    return JSONResponse(content=response.model_dump(), status_code=201)


@app.get("/movie")
async def get_movies(request: Request, filters: Filters = Depends(Filters())):
    result = await get_all(filters=filters)
    pagination = Pagination(page=filters.page, limit=filters.limit, total_count=result["total_count"], data=result["data"])
    response = APIResponsePaginated.model_validate(pagination.get_paginated_data())
    return JSONResponse(content=response.model_dump(), status_code=200)



@app.get("/movie/{movie_id}")
async def get_movie_info(request: Request, movie_id: UUID = Path(...)):
    data = await get(movie_id=movie_id)
    response = APIResponse(data=MovieResponse.model_validate(data))
    return JSONResponse(content=response.model_dump(), status_code=200)


@app.patch("/movie/{movie_id}")
async def update_movie_info(request: Request, payload: MovieUpdate, movie_id: UUID = Path(...)):
    data = await update(movie_id=movie_id, payload=payload)
    response = APIResponse(data=MovieResponse.model_validate(data))
    return JSONResponse(content=response.model_dump(), status_code=200)


@app.delete("/movie/{movie_id}")
async def delete_movie(request: Request, movie_id: UUID = Path(...)):
    await delete(movie_id=movie_id)
    return Response(status_code=204)


@app.get("/directors")
async def get_all_directors(request: Request):
    results = await list_directors()
    return JSONResponse(content={"success": True, "message": "Success", "data": results}, status_code=200)
