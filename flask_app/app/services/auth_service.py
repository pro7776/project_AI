import logging
import bcrypt
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..domain.entities import User
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Базовое исключение для ошибок аутентификации"""
    pass


class UserAlreadyExistsError(AuthServiceError):
    """Пользователь уже существует"""
    pass


class InvalidCredentialsError(AuthServiceError):
    """Неверные учётные данные"""
    pass


class AuthService:
    def __init__(self, session: Session):
        self._user_repo = UserRepository(session)

    def register(self, username: str, password: str) -> User:
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        if not password or len(password) < 4:
            raise ValueError("Пароль должен содержать не менее 4 символов")

        logger.info(f"Регистрация пользователя: {username}")

        try:
            existing = self._user_repo.get_by_username(username)
            if existing:
                logger.warning(f"Пользователь {username} уже существует")
                raise UserAlreadyExistsError(
                    f"Пользователь '{username}' уже существует")

            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = self._user_repo.create(username, hashed.decode('utf-8'))

            logger.info(
                f"Пользователь {username} зарегистрирован (ID: {user.id})")
            return user

        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных при регистрации: {e}")
            raise AuthServiceError(
                "Ошибка при сохранении пользователя в базе данных")

    def login(self, username: str, password: str) -> User:
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        if not password:
            raise ValueError("Пароль не может быть пустым")

        logger.info(f"Попытка входа: {username}")

        try:
            user = self._user_repo.get_by_username(username)
            if not user:
                logger.warning(f"Пользователь {username} не найден")
                raise InvalidCredentialsError(
                    "Неверное имя пользователя или пароль")

            if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
                logger.warning(f"Неверный пароль для пользователя {username}")
                raise InvalidCredentialsError(
                    "Неверное имя пользователя или пароль")

            logger.info(f"Успешный вход: {username}")
            return user

        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных при входе: {e}")
            raise AuthServiceError("Ошибка при проверке учётных данных")
