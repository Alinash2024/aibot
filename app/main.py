from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="AI News Bot API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Hello": "World"}
