import re
from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import date, datetime
from uuid import UUID


class Movie(BaseModel):
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[date] = None
    director: Optional[str] = None
    synopsis: Optional[str] = Field(None, max_length=1000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, multiple_of=0.25)
    review: Optional[str] = Field(None, max_length=1000)

    @field_validator("poster_url", mode="after")
    def validate_poster_url(cls, value):
        def is_valid_url(url: str) -> bool:
            url_pattern = re.compile(
                r'^(?:http|ftp)s?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$',
                re.IGNORECASE
            )

            return bool(url_pattern.match(url))
        
        if value and not is_valid_url(url=value):
            raise ValueError("Invalid URL")
        return value
    
    def model_dump(self, *, mode = 'python', include = None, exclude = None, context = None, by_alias = False, exclude_unset = False, exclude_defaults = False, exclude_none = False, round_trip = False, warnings = True, serialize_as_any = False):
        result = super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)
        result["release_date"] = self.release_date.isoformat() if self.release_date else None
        return result


class MovieUpdate(Movie):
    title: Optional[str] = None


class MovieResponse(Movie):
    id: UUID
    created_at: datetime
    updated_at: datetime


class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: MovieResponse

    def model_dump(self, *, mode = 'python', include = None, exclude = None, context = None, by_alias = False, exclude_unset = False, exclude_defaults = False, exclude_none = False, round_trip = False, warnings = True, serialize_as_any = False):
        result = super().model_dump(mode=mode, include=include, exclude=exclude, context=context, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings, serialize_as_any=serialize_as_any)
        
        result["data"]["id"] = str(self.data.id)
        result["data"]["release_date"] = self.data.release_date.isoformat() if self.data.release_date else None
        result["data"]["created_at"] = self.data.created_at.isoformat()
        result["data"]["updated_at"] = self.data.updated_at.isoformat()

        return result


class APIResponsePaginated(BaseModel):
    success: bool = True
    message: str = "Success"
    page: int
    limit: int
    prev_page: Optional[int]
    next_page: Optional[int]
    total_count: int
    page_count: int
    data: Union[List[MovieResponse], List]


class Filters:
    page: int = None
    limit: int = None
    release_year: int = None
    rating: int = None
    director: str = None
    search: str = None

    def __call__(self,
                 page: int = Query(1, ge=1),
                 limit: int = Query(10, ge=1),
                 release_year: int = Query(None, ge=1900, le=9999),
                 rating: int = Query(None, ge=1, le=5),
                 director: str = Query(None),
                 search: str = Query(None)):
        self.page = page
        self.limit = limit
        self.release_year = release_year
        self.rating = rating
        self.director = director
        self.search = search

        return self
