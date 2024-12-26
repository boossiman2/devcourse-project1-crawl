import os
import json
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas import movie
from app.models import models


logger = logging.getLogger(__name__)
JSON_PATH = os.path.join('app', 'data', 'crawl', 'raw', 'movies_data_country.json')

############################ MOVIE ############################
def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Movie).offset(skip).limit(limit).all()

def get_movies_by_country_name(db: Session, country_name: str):
    country = db.query(models.Country).filter(models.Country.name == country_name).first()
    if not country:
        bulk_insert_movies_from_json(db=db)
        country = db.query(models.Country).filter(models.Country.name == country_name).first()
    return country.movies[:5]

def bulk_insert_movies_from_json(db: Session, json_path: str = JSON_PATH):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Loaded JSON data: {data}")

        movies = data.get('movies', [])
        if not movies:
            logger.error('No movie data provided')
            raise HTTPException(status_code=400, detail="No movie data provided in JSON file")

        new_movies = []

        for movie_data in movies:
            movie_info = movie_data.get("movie", {})
            if not movie_info:
                logger.error("Movie data is incomplete or missing")
                raise HTTPException(status_code=400, detail="Movie data is incomplete or missing")

            # Create or fetch country
            country_name = movie_data.get("country")
            country = db.query(models.Country).filter(models.Country.name == country_name).first()

            # If country doesn't exist, add it to the DB
            if not country:
                country = models.Country(name=country_name)
                db.add(country)
                db.commit()  # Commit immediately to persist country
                db.refresh(country)  # Ensure the country is fully committed

            # Create or fetch genres
            genres = []
            for genre_name in movie_info.get("genres", []):
                genre = db.query(models.Genre).filter(models.Genre.name == genre_name).first()
                if not genre:
                    genre = models.Genre(name=genre_name)
                    db.add(genre)
                    db.commit()  # Commit immediately to persist country
                    db.refresh(genre)  # Ensure the country is fully committed

                genres.append(genre)

            # Create or fetch actors
            actors = []
            for actor_name in movie_info.get("actors", []):
                actor = db.query(models.Actor).filter(models.Actor.name == actor_name).first()
                if not actor:
                    actor = models.Actor(name=actor_name)
                    db.add(actor)
                    db.commit()  # Commit immediately to persist country
                    db.refresh(actor)  # Ensure the country is fully committed

                actors.append(actor)
            # score null 처리
            score = movie_info.get('score', 0.0)
            if not score or score == 'null':
                score = 0
            # Create movie
            db_movie = models.Movie(
                title=movie_info.get("title"),
                release_year=movie_info.get("release_year"),
                score=float(score),
                summary=movie_info.get("summary"),
                image_url=movie_info.get("image_url"),
                country=country,
                genres=genres,
                actors=actors
            )
            db.add(db_movie)
            new_movies.append(db_movie)

        db.commit()  # Commit all changes at once after all movies are added
        return {"message": "Movies successfully inserted", "count": len(new_movies)}

    except FileNotFoundError:
        logger.error("JSON file not found.")
        raise HTTPException(status_code=404, detail="JSON file not found")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON file.")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except IntegrityError as e:
        logger.error(f"IntegrityError: {e.orig}")
        db.rollback()  # Rollback on integrity error
        raise HTTPException(status_code=400, detail="Integrity error occurred while saving data.")
    except Exception as e:
        logger.error(f"Error saving movies: {e}")
        db.rollback()  # Rollback on any other error
        raise HTTPException(status_code=500, detail=f"Error saving movies: {str(e)}")

def delete_movie(db: Session, movie: movie.Movie):
    db.delete(movie)
    db.commit()