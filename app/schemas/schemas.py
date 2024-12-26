from pydantic import BaseModel

class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int

    class Config:
        orm_mode = True

class ActorBase(BaseModel):
    name: str

class ActorCreate(ActorBase):
    pass

class Actor(ActorBase):
    id: int

    class Config:
        orm_mode = True

class RankingBase(BaseModel):
    rank: int
    country_id: int
    movie_id: int

class RankingCreate(RankingBase):
    pass

class Ranking(RankingBase):
    id: int

    class Config:
        orm_mode = True
