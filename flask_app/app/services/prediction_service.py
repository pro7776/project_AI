import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from ..repositories.prediction_repository import PredictionRepository
from ..domain.interfaces import MLClient

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, session: Session, ml_client: MLClient):
        self._prediction_repo = PredictionRepository(session)
        self._ml_client = ml_client

    async def make_prediction(self, user_id: int, description: str) -> Dict[str, Any]:
        logger.info(f"Создание предсказания для пользователя {user_id}")

        prediction = await self._ml_client.predict(description)

        self._prediction_repo.create(
            user_id=user_id,
            input_data={"description": description},
            prediction=prediction
        )

        logger.info(f"Предсказание для пользователя {user_id} сохранено")

        return {
            "description": description,
            "prediction": prediction
        }

    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        logger.info(f"Получение истории для пользователя {user_id}")

        predictions = self._prediction_repo.get_by_user_id(user_id, limit)

        return [
            {
                "id": p.id,
                "input_data": p.input_data,
                "prediction": p.prediction,
                "created_at": p.created_at.isoformat()
            }
            for p in predictions
        ]
