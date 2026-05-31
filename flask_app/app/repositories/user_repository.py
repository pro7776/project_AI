import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..domain.entities import User
from ..domain.interfaces import UserRepository as IUserRepository
from ..models import User as UserModel

logger = logging.getLogger(__name__)


class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_username(self, username: str) -> Optional[User]:
        logger.info(f"Поиск пользователя по имени: {username}")
        user_model = self._session.query(UserModel).filter(
            UserModel.username == username
        ).first()

        if not user_model:
            logger.warning(f"Пользователь {username} не найден")
            return None

        return User(
            id=user_model.id,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            created_at=user_model.created_at
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        logger.info(f"Поиск пользователя по ID: {user_id}")
        user_model = self._session.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

        if not user_model:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            return None

        return User(
            id=user_model.id,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            created_at=user_model.created_at
        )

    def create(self, username: str, hashed_password: str) -> User:
        logger.info(f"Создание пользователя: {username}")
        user_model = UserModel(
            username=username,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        self._session.add(user_model)
        self._session.commit()
        self._session.refresh(user_model)

        logger.info(f"Пользователь {username} создан (ID: {user_model.id})")

        return User(
            id=user_model.id,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            created_at=user_model.created_at
        )
