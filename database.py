from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

# Use environment variable for database URL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()
metadata.reflect(bind=engine)  # This line reflects the current database structure

Base = declarative_base(metadata=metadata)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while creating tables: {e}")

if __name__ == "__main__":
    create_tables()
