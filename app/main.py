from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect

from app.database import EngineConn
from app.models.models import Base
from app.routers.routes import router

# 데이터베이스 연결 설정
engine = EngineConn().engine

# 비동기 컨텍스트 관리자 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행할 코드
    inspector = inspect(engine)
    if not inspector.has_table('movies'):
        Base.metadata.create_all(bind=engine)
    yield
    # 애플리케이션 종료 시 실행할 코드 (필요한 경우 추가)
    pass

# FastAPI 애플리케이션 생성 및 router 등록
app = FastAPI(lifespan=lifespan)
app.include_router(router)
# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory='app/templates')

# 루트 엔드포인트
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Welcome to Worldwide Movies"}
    )

# 영화, 배우, 장르 등의 라우트 설정
