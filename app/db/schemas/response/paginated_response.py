# paginated_response.py
from typing import List, Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    page: int
    limit: int
    total_items: int
    total_pages: int
    data: List[T]
