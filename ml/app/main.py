from fastapi import FastAPI
from app.recommender import router

app = FastAPI(title="ML Recommender Service")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
