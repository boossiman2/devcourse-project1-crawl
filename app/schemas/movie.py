from pydantic import BaseModel
from typing import List, Optional
from app.schemas.schemas import *

class MovieBase(BaseModel):
    title: str
    release_year: str
    score: float
    summary: Optional[str] = None
    image_url: Optional[str] = None
    genres: List[GenreCreate] = []
    actors: List[ActorCreate] = []

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True
        
class BulkInsertMovies(BaseModel):
    movies: List[MovieCreate]