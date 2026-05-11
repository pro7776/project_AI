from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()


class RecommendRequest(BaseModel):
    query: str
    type: str   # "description", "title", "author"


class Book(BaseModel):
    title: str
    author: str
    description: str


ML_URL = os.getenv("ML_SERVICE_URL", "http://ml:8002")


@router.post("/recommend", response_model=list[Book])
async def recommend(request: RecommendRequest):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ML_URL}/predict",
                json={"query": request.query, "type": request.type},
                timeout=5.0
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("books", [])
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"ML service error: {str(e)}")
