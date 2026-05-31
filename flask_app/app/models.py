from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from .database import db


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    author = Column(String(500))
    year = Column(Float)
    genre = Column(String(200))
    description = Column(Text)
    rating = Column(Float)
    rating_count = Column(Integer)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    input_data = Column(JSON, nullable=False)
    prediction = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
