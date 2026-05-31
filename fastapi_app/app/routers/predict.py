import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories.prediction_repository import PredictionRepository
from ..services.prediction_service import PredictionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["prediction"])


class PredictRequest(BaseModel):
    user_id: int = Field(default=0, description="ID пользователя")
    description: str = Field(
        default="", description="Описание книги (необязательно)")
    title: Optional[str] = Field(default=None, description="Название книги")
    genre: Optional[str] = Field(default=None, description="Жанр")
    author: Optional[str] = Field(default=None, description="Автор")
    min_rating: float = Field(default=0, ge=0, le=5,
                              description="Минимальный рейтинг")
    max_year: Optional[int] = Field(
        default=None, description="Год издания (до)")

    @validator('description')
    def validate_description(cls, v: str) -> str:
        return v.strip() if v else ""


class BookResponse(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    rating: float
    description: str
    similarity: float = 0.0


class PredictResponse(BaseModel):
    books: List[BookResponse] = []
    message: str = ""
    count: int = 0


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        400: {"description": "Ошибка валидации"},
        500: {"description": "Внутренняя ошибка сервера"},
        503: {"description": "Сервис недоступен"}
    }
)
async def predict(request: PredictRequest, db: Session = Depends(get_db)):
    """Поиск книг по описанию и фильтрам"""
    logger.info(
        f"Получен запрос от user_id={request.user_id}: "
        f"description='{request.description[:50] if request.description else ''}', "
        f"title='{request.title}', genre='{request.genre}'"
    )

    try:
        prediction_service = PredictionService()
        result = await prediction_service.predict(
            description=request.description,
            title=request.title,
            genre=request.genre,
            author=request.author,
            min_rating=request.min_rating,
            max_year=request.max_year
        )

        # Сохраняем предсказание в БД
        try:
            repo = PredictionRepository()
            await repo.save_prediction(
                user_id=request.user_id,
                input_data=request.dict(),
                prediction=result.get('message', '')
            )
            logger.info(
                f"Предсказание сохранено для user_id={request.user_id}")
        except Exception as e:
            logger.warning(f"Не удалось сохранить предсказание в БД: {e}")

        logger.info(
            f"Предсказание успешно возвращено: найдено {result.get('count', 0)} книг")
        return PredictResponse(
            books=result.get('books', []),
            message=result.get('message', ''),
            count=result.get('count', 0)
        )

    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "message": str(
                e), "code": "VALIDATION_ERROR"}
        )
    except ConnectionError as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "message": "База данных временно недоступна",
                    "code": "DB_CONNECTION_ERROR"}
        )
    except Exception as e:
        logger.error(
            f"Непредвиденная ошибка при предсказании: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": "Внутренняя ошибка сервера",
                    "code": "INTERNAL_ERROR"}
        )


@router.get("/genres")
async def get_genres():
    """Получить список всех жанров"""
    try:
        prediction_service = PredictionService()
        genres = await prediction_service.get_genres()
        logger.info(f"Возвращено {len(genres)} жанров")
        return genres
    except Exception as e:
        logger.error(f"Ошибка получения жанров: {e}")
        return []


@router.get("/authors")
async def get_authors():
    """Получить список всех авторов"""
    try:
        prediction_service = PredictionService()
        authors = await prediction_service.get_authors()
        logger.info(f"Возвращено {len(authors)} авторов")
        return authors[:100]  # Ограничиваем количество
    except Exception as e:
        logger.error(f"Ошибка получения авторов: {e}")
        return []
