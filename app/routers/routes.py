import logging
from pathlib import Path
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.Service.movie import *
from app.database import EngineConn
from app.utils.visualizer import Visualizer

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
@router.get("/movies/{country_name}/", response_model=list[movie.MovieBase])
def fetch_movies_by_country(country_name: str, db: Session = Depends(get_db)):
    logger.debug(f"Looking for country: {country_name}")
    country = db.query(models.Country).filter(models.Country.name == country_name).first()
    if not country:
        logger.warning(f"Country {country_name} not found. Attempting to bulk insert movies.")
        bulk_insert_movies_from_json(db=db)
        country = db.query(models.Country).filter(models.Country.name == country_name).first()
        if not country:
            logger.error(f"Country {country_name} still not found after bulk insert.")
            raise HTTPException(status_code=404, detail=f"Country {country_name} not found.")
    logger.debug(f"Found country: {country.name} with movies: {country.movies}")
    # visualizer 호출 및 HTML 파일 생성
    visualizer = Visualizer(db=db, country_name=country_name)
    output_path = visualizer.create_combined_html()
    # 생성된HTML 파일 읽기 및 반환
    html_content = Path(output_path).read_text(encoding='utf-8')
    return HTMLResponse(content=html_content, status_code=200)
