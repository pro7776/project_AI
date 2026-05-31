from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from .database import Base


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    input_data = Column(JSON, nullable=False)
    prediction = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
