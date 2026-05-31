import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    logger.info("Проверка здоровья сервиса")
    return {"status": "ok", "service": "ml-api"}


@router.get("/ready")
async def readiness_check():
    from ..services.model_service import load_model

    try:
        load_model()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Сервис не готов: {e}")
        return {"status": "not_ready", "error": str(e)}
