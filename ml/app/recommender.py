from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class PredictRequest(BaseModel):
    query: str
    type: str


class Book(BaseModel):
    title: str
    author: str
    description: str


# Заглушка: фиксированные книги
MOCK_BOOKS = [
    Book(title="Война и мир", author="Лев Толстой",
         description="Исторический роман о русском обществе в эпоху Наполеоновских войн."),
    Book(title="Преступление и наказание", author="Фёдор Достоевский",
         description="Психологический роман о студенте Раскольникове."),
    Book(title="Анна Каренина", author="Лев Толстой",
         description="Трагическая история любви замужней женщины."),
]


@router.post("/predict")
async def predict(request: PredictRequest):
    # В реальном сервисе здесь будет вызов модели (например, эмбеддинги + FAISS)
    # Сейчас просто возвращаем первые 3 книги
    return {"books": MOCK_BOOKS[:3]}
