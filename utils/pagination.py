from math import ceil
from typing import Union, Dict


class Pagination:
    def __init__(self, page, limit, total_count, data):
        self._total_pages = ceil(total_count/limit)
        self._page = page
        self._count = total_count
        self._page_size = limit
        self.data = data

    @property
    def _next(self) -> Union[int, object]:
        if int(self._total_pages) - int(self._page) > 0:
            return self._page + 1
        return

    @property
    def _previous(self) -> Union[int, object]:
        if int(self._total_pages) - int(self._page) >= 0 and int(self._page) - 1 > 0:
            return int(self._page) - 1
        return None

    def get_paginated_data(self) -> Dict:
        data = dict(
            total_count=self._count,
            page=self._page,
            limit=self._page_size,
            next_page=self._next,
            prev_page=self._previous,
            page_count=self._total_pages,
            data=self.data
        )
        return data
