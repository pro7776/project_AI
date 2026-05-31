from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    id: Optional[int]
    username: str
    hashed_password: str
    created_at: datetime


@dataclass
class Prediction:
    id: Optional[int]
    user_id: int
    input_data: Dict[str, Any]
    prediction: str
    created_at: datetime
