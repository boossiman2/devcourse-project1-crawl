import logging
from fastapi import Depends, APIRouter, HTTPException
from app.Service.movie import *
from app.database import EngineConn

router = APIRouter()
engine_conn = EngineConn()
logger = logging.getLogger(__name__)
# Dependency for getting a database session

def get_db():
    '''
    FastAPI 의존성 주입을 통해 데이터베이스 세션을 생성하고 관리.
    '''
    db = engine_conn.get_session()
    try:
        yield db
    finally:
        db.close()

# Endpoint to fetch movies by country name
@router.get("/movies/{country_name}", response_model=list[schemas.MovieSchema])
def fetch_movies_by_country(country_name: str, db: Session = Depends(get_db)):
    try:
        movies = get_movies_by_country_name(db, country_name)
        if not movies:
            raise HTTPException(status_code=404, detail=f"No movies found for country: {country_name}")
        return movies
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/movies/bulk_insert", response_model=List[schemas.Movie])
def bulk_insert_movies_api(movies: schemas.BulkInsertMovies, db: Session = Depends(get_db)):
    try:
        inserted_movies = bulk_insert_movies(db, movies.movies)
        return inserted_movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))