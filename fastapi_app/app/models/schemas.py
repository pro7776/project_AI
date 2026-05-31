from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str
    genre: Optional[str] = None
    author: Optional[str] = None
    min_rating: float = 0
    max_year: Optional[int] = None
    top_k: int = 20


class BookResponse(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    rating: float
    description: str
    similarity: float
