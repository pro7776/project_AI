import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model = None


def load_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Загрузка модели SentenceTransformer...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("Модель загружена")
    return _model


def get_model_info() -> dict:
    model = load_model()
    return {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "version": "1.0.0",
        "framework": "sentence-transformers",
        "description": "Multilingual model for semantic similarity search",
        "input_type": "text",
        "output_type": "embedding (384 dimensions)"
    }
