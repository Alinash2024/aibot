from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# Создаём базовый класс
Base = declarative_base()

class NewsItem(Base):
    __tablename__ = 'news_items'
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    summary = Column(Text)
    source = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text)

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)