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

# 엔드포인트에서 Session 의존성 사용
@router.get("/movies/{country_name}", response_model=list[schemas.MovieSchema])
def fetch_movies_by_country(country_name: str, db: Session = Depends(get_db)):
    try:
        movies = get_movies_by_country_name(db, country_name)
        if not movies:
            raise HTTPException(status_code=404, detail=f"No movies found for country: {country_name}")
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to create a movie
@router.post("/movies", response_model=schemas.MovieSchema)
def create_new_movie(movie: schemas.MovieSchema, db: Session = Depends(get_db)):
    try:
        return create_movie(db, movie)
    except Exception as e:
        logger.error(f"Error creating movie: {e}")
        raise HTTPException(status_code=500, detail=str(e))