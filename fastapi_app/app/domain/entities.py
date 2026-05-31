from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class PredictionRecord:
    id: int
    user_id: int
    input_data: Dict[str, Any]
    prediction: str
    created_at: datetime
