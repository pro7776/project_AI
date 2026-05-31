import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ..domain.entities import Prediction
from ..domain.interfaces import PredictionRepository as IPredictionRepository
from ..models import Prediction as PredictionModel

logger = logging.getLogger(__name__)


class PredictionRepository(IPredictionRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(self, user_id: int, input_data: Dict[str, Any], prediction: str) -> Prediction:
        logger.info(f"Сохранение предсказания для пользователя {user_id}")

        prediction_model = PredictionModel(
            user_id=user_id,
            input_data=input_data,
            prediction=prediction,
            created_at=datetime.utcnow()
        )
        self._session.add(prediction_model)
        self._session.commit()
        self._session.refresh(prediction_model)

        logger.info(f"Предсказание сохранено (ID: {prediction_model.id})")

        return Prediction(
            id=prediction_model.id,
            user_id=prediction_model.user_id,
            input_data=prediction_model.input_data,
            prediction=prediction_model.prediction,
            created_at=prediction_model.created_at
        )

    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Prediction]:
        logger.info(
            f"Получение истории предсказаний для пользователя {user_id}")

        predictions = self._session.query(PredictionModel).filter(
            PredictionModel.user_id == user_id
        ).order_by(PredictionModel.created_at.desc()).limit(limit).all()

        logger.info(f"Найдено {len(predictions)} предсказаний")

        return [
            Prediction(
                id=p.id,
                user_id=p.user_id,
                input_data=p.input_data,
                prediction=p.prediction,
                created_at=p.created_at
            )
            for p in predictions
        ]
