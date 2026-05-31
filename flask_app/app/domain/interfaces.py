from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .entities import User, Prediction


class UserRepository(ABC):
    """Репозиторий для работы с пользователями"""

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по имени пользователя

        Args:
            username: Имя пользователя

        Returns:
            User или None, если пользователь не найден
        """
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            User или None, если пользователь не найден
        """
        ...

    @abstractmethod
    def create(self, username: str, hashed_password: str) -> User:
        """
        Создать нового пользователя

        Args:
            username: Имя пользователя
            hashed_password: Хешированный пароль

        Returns:
            Созданный объект User
        """
        ...


class PredictionRepository(ABC):
    """Репозиторий для работы с предсказаниями"""

    @abstractmethod
    def create(self, user_id: int, input_data: Dict[str, Any], prediction: str) -> Prediction:
        """
        Сохранить предсказание в базу данных

        Args:
            user_id: ID пользователя
            input_data: Входные данные запроса
            prediction: Результат предсказания

        Returns:
            Созданный объект Prediction
        """
        ...

    @abstractmethod
    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[Prediction]:
        """
        Получить историю предсказаний пользователя

        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей

        Returns:
            Список предсказаний пользователя
        """
        ...


class MLClient(ABC):
    """Клиент для взаимодействия с ML сервисом"""

    @abstractmethod
    async def predict(self, description: str) -> str:
        """
        Отправить запрос на предсказание в ML сервис

        Args:
            description: Описание книги для поиска

        Returns:
            Строка с результатами поиска

        Raises:
            MLClientConnectionError: При ошибке подключения
            MLClientTimeoutError: При таймауте
            MLClientResponseError: При ошибке в ответе сервиса
        """
        ...

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Получить информацию о ML модели

        Returns:
            Словарь с информацией о модели
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Проверить доступность ML сервиса

        Returns:
            True если сервис доступен, иначе False
        """
        ...
