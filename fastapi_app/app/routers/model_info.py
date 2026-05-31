import logging
from fastapi import APIRouter

from ..services.model_service import get_model_info

logger = logging.getLogger(__name__)
router = APIRouter(tags=["model-info"])


@router.get("/model-info")
async def model_info():
    logger.info("Запрос информации о модели")
    return get_model_info()
