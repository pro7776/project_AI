import logging
import sys
from fastapi import FastAPI, HTTPException
from .models.schemas import SearchRequest, BookResponse
from .services.search_service import search_books, get_genres, get_authors
from .services.embedding_service import load_books_and_embeddings
from .database import get_all_books

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Model Service")


@app.on_event("startup")
async def startup_event():
    """При старте сервиса загружаем данные"""
    logger.info("Запуск ML сервиса")
    try:
        load_books_and_embeddings(get_all_books)
        logger.info("ML сервис готов к работе")
    except Exception as e:
        logger.error(f"Ошибка при загрузке: {e}")
        raise


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/search", response_model=list[BookResponse])
async def search(request: SearchRequest):
    """Поиск книг по текстовому запросу"""
    logger.info(f"Получен поисковый запрос: {request.query}")
    try:
        results = search_books(request)
        return results
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/genres")
async def genres():
    """Получить список всех жанров"""
    return get_genres()


@app.get("/authors")
async def authors():
    """Получить список всех авторов"""
    return get_authors()
