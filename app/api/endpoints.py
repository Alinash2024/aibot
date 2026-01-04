from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Source, Keyword, Post, SessionLocal, NewsItem
from app.api.schemas import Source as SourceSchema, SourceCreate, SourceUpdate, Keyword as KeywordSchema, KeywordCreate, \
    KeywordUpdate, Post as PostSchema, GeneratePostRequest
from app.tasks import generate_post_task
from typing import List

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/sources/", response_model=List[SourceSchema])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = db.query(Source).offset(skip).limit(limit).all()
    return sources


@router.post("/sources/", response_model=SourceSchema)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/sources/{source_id}", response_model=SourceSchema)
def read_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/sources/{source_id}", response_model=SourceSchema)
def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    for key, value in source.dict(exclude_unset=True).items():
        setattr(db_source, key, value)

    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(source)
    db.commit()
    return {"detail": "Source deleted"}



@router.get("/keywords/", response_model=List[KeywordSchema])
def read_keywords(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    keywords = db.query(Keyword).offset(skip).limit(limit).all()
    return keywords


@router.post("/keywords/", response_model=KeywordSchema)
def create_keyword(keyword: KeywordCreate, db: Session = Depends(get_db)):
    db_keyword = Keyword(**keyword.dict())
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.get("/keywords/{keyword_id}", response_model=KeywordSchema)
def read_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword


@router.put("/keywords/{keyword_id}", response_model=KeywordSchema)
def update_keyword(keyword_id: int, keyword: KeywordUpdate, db: Session = Depends(get_db)):
    db_keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not db_keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    for key, value in keyword.dict(exclude_unset=True).items():
        setattr(db_keyword, key, value)

    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.delete("/keywords/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    db.delete(keyword)
    db.commit()
    return {"detail": "Keyword deleted"}



@router.get("/posts/", response_model=List[PostSchema])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts


@router.get("/posts/{post_id}", response_model=PostSchema)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



@router.post("/generate/", summary="Start generating a post manually")
def manual_generate_post(request: GeneratePostRequest, db: Session = Depends(get_db)):
    news_item = db.query(NewsItem).filter(NewsItem.id == request.news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")

    result = generate_post_task.delay(news_item.id)

    return {"task_id": result.id, "message": f"Generation started for news {request.news_id}"}