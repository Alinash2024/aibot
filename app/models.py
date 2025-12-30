from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import uuid

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    url = Column(String)
    summary = Column(String)
    source = Column(String, nullable=False)
    published_at = Column(DateTime)
    raw_text = Column(String)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)  # URL сайта или @username Telegram-канала
    source_type = Column(String, nullable=False)  # 'site' или 'tg'
    enabled = Column(Boolean, default=True)


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    news_id = Column(String, ForeignKey("news_items.id"))
    generated_text = Column(String)
    published_at = Column(DateTime)
    status = Column(String, default='new')  # 'new', 'generated', 'published', 'failed'


# Подключение к БД (пример с SQLite)
DATABASE_URL = "sqlite:///./aibot.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)