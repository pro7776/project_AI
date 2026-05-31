import logging
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..config import config

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PredictionRepository:
    def __init__(self):
        self._engine: Optional[Any] = None
        self._async_session: Optional[Any] = None
        self._init_engine()

    def _init_engine(self) -> None:
        try:
            async_db_url = config.database_url.replace(
                'postgresql://', 'postgresql+asyncpg://')
            self._engine = create_async_engine(async_db_url)
            self._async_session = sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False)
            logger.info("Подключение к базе данных установлено")
        except Exception as e:
            error_msg = f"Не удалось подключиться к базе данных: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)

    async def save_prediction(self, user_id: int, input_data: Dict[str, Any], prediction: str) -> None:
        """Сохранение предсказания в БД"""
        if user_id < 0:
            error_msg = "user_id не может быть отрицательным"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Сохраняем только краткое сообщение (первые 500 символов)
        prediction_str = (
            prediction[:500] + '...') if len(prediction) > 500 else prediction

        # Сохраняем только описание из input_data
        description = input_data.get('description', '')[:200] if isinstance(
            input_data, dict) else str(input_data)[:200]

        logger.info(f"Сохранение предсказания для пользователя {user_id}")

        try:
            if self._async_session is None:
                error_msg = "Сессия базы данных не инициализирована"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg)

            async with self._async_session() as session:
                async with session.begin():
                    await session.execute(
                        text("""
                            INSERT INTO predictions (user_id, input_data, prediction, created_at)
                            VALUES (:user_id, :input_data, :prediction, NOW())
                        """),
                        {
                            "user_id": user_id,
                            "input_data": json.dumps({"description": description}, ensure_ascii=False),
                            "prediction": prediction_str
                        }
                    )
            logger.info("Предсказание успешно сохранено")
        except Exception as e:
            logger.error(f"Ошибка при сохранении: {e}")
            raise

    async def get_all_books(self) -> List[Dict[str, Any]]:
        """Загрузка всех книг из базы данных"""
        logger.info("Загрузка всех книг из базы данных")

        try:
            if self._async_session is None:
                error_msg = "Сессия базы данных не инициализирована"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg)

            async with self._async_session() as session:
                result = await session.execute(
                    text("""
                        SELECT id, title, author, year, genre, description, rating 
                        FROM books 
                        ORDER BY id
                    """)
                )
                rows = result.fetchall()

                if not rows:
                    logger.warning("База данных книг пуста")
                    return []

                logger.info(f"Загружено {len(rows)} книг")

                books: List[Dict[str, Any]] = []
                for row in rows:
                    books.append({
                        "id": row[0],
                        "title": row[1] if row[1] else "Без названия",
                        "author": row[2] if row[2] else "Автор неизвестен",
                        "year": row[3] if row[3] else 0,
                        "genre": row[4] if row[4] else "Не указан",
                        "description": row[5] if row[5] else "",
                        "rating": float(row[6]) if row[6] else 0.0
                    })

                return books
        except Exception as e:
            logger.error(f"Ошибка при загрузке книг: {e}")
            raise
