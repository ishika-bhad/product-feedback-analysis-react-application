from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config.settings import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import Base and models to register them on Base.metadata
    from backend.app.models.base import Base
    from backend.app.models.product import Product
    from backend.app.models.feedback import Feedback
    
    Base.metadata.create_all(bind=engine)
