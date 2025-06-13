from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import os
import time 
from sqlalchemy.exc import OperationalError

username = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
host = os.getenv('POSTGRES_HOST', 'localhost')
port = os.getenv('POSTGRES_PORT', 5432)
database = os.getenv('POSTGRES_NAME', 'default')

engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Likes(Base):
    __tablename__ = 'likes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(UUID(as_uuid=True))
    video_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Dislikes(Base):
    __tablename__ = 'dislikes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(UUID(as_uuid=True))
    video_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Comments(Base):
    __tablename__ = 'comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(UUID(as_uuid=True))
    video_id = Column(UUID(as_uuid=True))
    content = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SubscriptionEntry(Base):
    __tablename__ = 'subscription_entry'

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
    user_id = Column(UUID(as_uuid=True))
    channel_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    

def create_tables_with_retry(engine, Base, retries=5):
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine, checkfirst=True)
            print("Tables created.")
            return
        except OperationalError as e:
            print(f"DB not ready (attempt {attempt + 1}): {e}")
            time.sleep(2)
    raise Exception("Failed to create tables after several retries")   

create_tables_with_retry(engine, Base)
