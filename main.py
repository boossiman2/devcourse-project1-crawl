from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import inspect
from database import EngineConn
from models import Base

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

# FastAPI 애플리케이션 생성
app = FastAPI(lifespan=lifespan)

# 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "영화 API에 오신 것을 환영합니다!"}

# 영화, 배우, 장르 등의 라우트 설정
