import logging
import httpx
from typing import Dict, Any

from ..config import config
from ..domain.interfaces import MLClient as IMLClient

logger = logging.getLogger(__name__)


class MLClientError(Exception):
    """Базовое исключение для ошибок ML клиента"""
    pass


class MLClientConnectionError(MLClientError):
    """Ошибка подключения к ML сервису"""
    pass


class MLClientTimeoutError(MLClientError):
    """Таймаут при запросе к ML сервису"""
    pass


class MLClientResponseError(MLClientError):
    """Ошибка в ответе ML сервиса"""
    pass


class MLClient(IMLClient):
    def __init__(self, timeout: float = 30.0):
        self._base_url = config.ml_service_url
        self._timeout = timeout

    async def predict(self, description: str) -> str:
        if not description or not description.strip():
            raise ValueError("Описание книги не может быть пустым")

        logger.info(f"Отправка запроса к ML API: {description[:50]}...")

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/predict",
                    json={"description": description.strip()}
                )

                if response.status_code == 422:
                    logger.error(f"Ошибка валидации: {response.text}")
                    raise MLClientResponseError(
                        "Неверный формат запроса к ML сервису")

                if response.status_code == 500:
                    logger.error(
                        f"Внутренняя ошибка ML сервиса: {response.text}")
                    raise MLClientResponseError(
                        "ML сервис вернул внутреннюю ошибку")

                response.raise_for_status()
                data = response.json()

                if "prediction" not in data:
                    logger.error(f"Неожиданный формат ответа: {data}")
                    raise MLClientResponseError(
                        "Неверный формат ответа от ML сервиса")

                logger.info(f"Получен ответ от ML API")
                return data["prediction"]

        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к ML API: {e}")
            raise MLClientTimeoutError(
                f"Превышено время ожидания ({self._timeout} сек)")
        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения к ML API: {e}")
            raise MLClientConnectionError(
                "Не удалось подключиться к ML сервису")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP ошибка: {e.response.status_code} - {e.response.text}")
            raise MLClientResponseError(
                f"ML сервис вернул ошибку {e.response.status_code}")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при запросе к ML API: {e}")
            raise MLClientError(f"Ошибка при обращении к ML сервису: {str(e)}")

    async def get_model_info(self) -> Dict[str, Any]:
        logger.info("Запрос информации о модели")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self._base_url}/model-info")
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при получении информации о модели: {e}")
            return {"error": "timeout", "message": "Сервис временно недоступен"}
        except httpx.ConnectError as e:
            logger.error(
                f"Ошибка подключения при получении информации о модели: {e}")
            return {"error": "connection", "message": "Не удалось подключиться к ML сервису"}
        except Exception as e:
            logger.error(f"Ошибка при получении информации о модели: {e}")
            return {"error": "unknown", "message": str(e)}

    async def health_check(self) -> bool:
        logger.info("Проверка здоровья ML API")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка при проверке здоровья ML API: {e}")
            return False
