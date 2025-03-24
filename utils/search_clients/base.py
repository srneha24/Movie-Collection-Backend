from abc import abstractmethod
from uuid import UUID

from schemas import Filters


class SearchClient(object):
  client = None

  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(SearchClient, cls).__new__(cls)
    return cls.instance
  
  @abstractmethod
  async def create_index(self):
     pass
  
  @abstractmethod
  async def insert(self, data: dict):
    pass
  
  @abstractmethod
  async def update(self, document_id: UUID, data: dict):
    pass
  
  @abstractmethod
  async def get(self, document_id: UUID) -> dict:
    pass
  
  @abstractmethod
  async def get_all(self, filters: Filters) -> dict:
    pass
  
  @abstractmethod
  async def delete(self, document_id: UUID):
    pass
  
  @abstractmethod
  async def get_all_directors(self) -> list:
    pass
