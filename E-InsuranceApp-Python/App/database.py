from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Core.settings import settings


engine = create_engine(settings.DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DataBaseConnection:
    def get_db_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()