import logging
from sqlalchemy.orm import Session
from .. import db
from ..models import Book

logger = logging.getLogger(__name__)


class BookNotFoundError(Exception):
    pass


class BookServiceError(Exception):
    pass


def get_db_session():
    """Получить сессию БД"""
    return Session(db.engine)


def get_all_books():
    """Получить все книги из PostgreSQL"""
    logger.info("Получение всех книг из базы данных")
    try:
        with get_db_session() as session:
            books = session.query(Book).order_by(Book.id).all()
            logger.info(f"Получено {len(books)} книг")
            return books
    except Exception as e:
        logger.error(f"Ошибка при получении книг: {e}")
        raise BookServiceError(f"Не удалось получить книги: {str(e)}")


def get_book_by_id(book_id: int):
    """Получить книгу по ID"""
    logger.info(f"Поиск книги с ID: {book_id}")
    try:
        with get_db_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise BookNotFoundError(f"Книга с ID {book_id} не найдена")
            return book
    except BookNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при поиске книги: {e}")
        raise BookServiceError(f"Ошибка при поиске книги: {str(e)}")


def add_book(title: str, author: str, year: float, genre: str,
             description: str, rating: float, rating_count: int):
    """Добавить новую книгу"""
    logger.info(f"Добавление книги: {title}")

    if not title or not title.strip():
        raise ValueError("Название книги не может быть пустым")

    try:
        with get_db_session() as session:
            new_book = Book(
                Title=title.strip(),
                Author=author.strip() if author else None,
                Year=year if year else None,
                Genre=genre.strip() if genre else None,
                Description=description.strip() if description else None,
                Rating=rating if rating else 0,
                Rating_Count=rating_count if rating_count else 0
            )
            session.add(new_book)
            session.commit()
            session.refresh(new_book)
            logger.info(f"Книга '{title}' добавлена (ID: {new_book.id})")
            return new_book
    except Exception as e:
        logger.error(f"Ошибка при добавлении книги: {e}")
        raise BookServiceError(f"Не удалось добавить книгу: {str(e)}")


def update_book(book_id: int, title: str, author: str, year: float,
                genre: str, description: str, rating: float, rating_count: int):
    """Обновить книгу"""
    logger.info(f"Обновление книги {book_id}: {title}")

    try:
        with get_db_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise BookNotFoundError(f"Книга с ID {book_id} не найдена")

            book.Title = title.strip()
            book.Author = author.strip() if author else None
            book.Year = year if year else None
            book.Genre = genre.strip() if genre else None
            book.Description = description.strip() if description else None
            book.Rating = rating if rating else 0
            book.Rating_Count = rating_count if rating_count else 0

            session.commit()
            logger.info(f"Книга {book_id} обновлена")
    except BookNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении книги: {e}")
        raise BookServiceError(f"Не удалось обновить книгу: {str(e)}")


def delete_book(book_id: int):
    """Удалить книгу"""
    logger.info(f"Удаление книги {book_id}")

    try:
        with get_db_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise BookNotFoundError(f"Книга с ID {book_id} не найдена")

            session.delete(book)
            session.commit()
            logger.info(f"Книга {book_id} удалена")
    except BookNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении книги: {e}")
        raise BookServiceError(f"Не удалось удалить книгу: {str(e)}")
