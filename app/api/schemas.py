from pydantic import BaseModel
from typing import Optional

class SourceBase(BaseModel):
    name: str
    url: str
    source_type: str
    enabled: bool = True

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = None
    enabled: Optional[bool] = None

class Source(SourceBase):
    id: int

    class Config:
        from_attributes = True

class KeywordBase(BaseModel):
    word: str

class KeywordCreate(KeywordBase):
    pass

class KeywordUpdate(BaseModel):
    word: Optional[str] = None

class Keyword(KeywordBase):
    id: int

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    generated_text: Optional[str] = None
    status: str

class Post(PostBase):
    id: int
    news_id: str

    class Config:
        from_attributes = True

class GeneratePostRequest(BaseModel):
    news_id: str