from sqlalchemy.orm import Session
from schemas import *
from models import *
from database import EngineConn

# engineconn 클래스 인스턴스를 생성하고 세션 팩토리를 가져옵니다.
engine = EngineConn()
SessionLocal = engine.get_session

############################ MOVIE ############################
def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Movie).offset(skip).limit(limit).all()

def create_movie(db: Session, movie: schemas.MovieSchema):
    db_movie = models.Movie(
        title=movie.title,
        summary=movie.summary,
        score=movie.score,
        rank=movie.rank,
        country_id=movie.country.id
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    
    # Many-to-many relationships (genres and actors)
    db_movie.genres = [db.query(models.Genre).get(genre.id) for genre in movie.genres]
    db_movie.actors = [db.query(models.Actor).get(actor.id) for actor in movie.actors]
    db.commit()
    return db_movie

def update_movie(db: Session, movie: models.Movie, updated_movie: schemas.MovieSchema):
    for key, value in updated_movie.dict(exclude={"country", "genres", "actors"}).items():
        setattr(movie, key, value)
    
    # Update relationships
    movie.country_id = updated_movie.country.id
    movie.genres = [db.query(models.Genre).get(genre.id) for genre in updated_movie.genres]
    movie.actors = [db.query(models.Actor).get(actor.id) for actor in updated_movie.actors]
    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie: models.Movie):
    db.delete(movie)
    db.commit()

############################ ACTOR ############################
def get_actor(db: Session, actor_id: int):
    return db.query(models.Actor).filter(models.Actor.id == actor_id).first()

def get_actors(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Actor).offset(skip).limit(limit).all()

def create_actor(db: Session, actor: schemas.ActorSchema):
    db_actor = models.Actor(name=actor.name)
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor

def update_actor(db: Session, actor: models.Actor, updated_actor: schemas.ActorSchema):
    actor.name = updated_actor.name
    db.commit()
    db.refresh(actor)
    return actor

def delete_actor(db: Session, actor: models.Actor):
    db.delete(actor)
    db.commit()

############################ GENRE ############################
def get_genre(db: Session, genre_id: int):
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()

def get_genres(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Genre).offset(skip).limit(limit).all()

def create_genre(db: Session, genre: schemas.GenreSchema):
    db_genre = models.Genre(name=genre.name)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

def update_genre(db: Session, genre: models.Genre, updated_genre: schemas.GenreSchema):
    genre.name = updated_genre.name
    db.commit()
    db.refresh(genre)
    return genre

def delete_genre(db: Session, genre: models.Genre):
    db.delete(genre)
    db.commit()

############################ COUNTRY ############################
def get_country(db: Session, country_id: int):
    return db.query(models.Country).filter(models.Country.id == country_id).first()

def get_countries(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Country).offset(skip).limit(limit).all()

def create_country(db: Session, country: schemas.CountrySchema):
    db_country = models.Country(name=country.name)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

def update_country(db: Session, country: models.Country, updated_country: schemas.CountrySchema):
    country.name = updated_country.name
    db.commit()
    db.refresh(country)
    return country

def delete_country(db: Session, country: models.Country):
    db.delete(country)
    db.commit()

############################ ERROR CHECK ############################
# 1. Relationships like genres and actors in `create_movie` must exist in the database; ensure they are pre-created.
# 2. Updating or deleting relationships requires careful handling to avoid orphaned rows or integrity errors.
# 3. Ensure proper error handling for `get` methods to handle non-existent IDs gracefully.
# 4. Validate incoming schemas before processing to avoid unexpected runtime errors.
