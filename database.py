import os
from typing import Final
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DB_USER: Final = os.getenv('DB_USER')
DB_PASSWD: Final = os.getenv('DB_PASSWD')
DB_HOST: Final = os.getenv("DB_HOST")
DB_PORT: Final = os.getenv('DB_PORT')
DB_NAME: Final = os.getenv('DB_NAME')

class EngineConn:
    def __init__(self):
        load_dotenv()
        self.engine = create_engine(
            f'mysql+pymysql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8',
            echo=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

