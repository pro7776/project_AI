import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
from .model_service import load_model

logger = logging.getLogger(__name__)


class PredictionServiceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ModelNotLoadedError(PredictionServiceError):
    def __init__(self, message: str = "Модель не загружена"):
        super().__init__(message)


class NoBooksFoundError(PredictionServiceError):
    def __init__(self, message: str = "В базе данных нет книг"):
        super().__init__(message)


class PredictionService:
    def __init__(self):
        self._model = None
        self._books_cache = None
        self._embeddings_cache = None
        self._genres_cache = None
        self._authors_cache = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            self._model = load_model()
            if self._model is None:
                raise ModelNotLoadedError("Не удалось загрузить модель")
            logger.info("Модель успешно загружена")
        except ModelNotLoadedError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise ModelNotLoadedError(f"Ошибка загрузки модели: {str(e)}")

    async def load_books(self) -> tuple:
        if self._books_cache is not None:
            return self._books_cache, self._embeddings_cache

        try:
            from ..repositories.prediction_repository import PredictionRepository
            repo = PredictionRepository()
            books = await repo.get_all_books()

            if not books:
                logger.error("База данных книг пуста")
                raise NoBooksFoundError("В базе данных нет книг")

            descriptions = []
            for book in books:
                desc = book.get('description') or book.get('title') or ''
                descriptions.append(str(desc) if desc else '')

            logger.info(f"Вычисление эмбеддингов для {len(books)} книг...")
            self._embeddings_cache = self._model.encode(
                descriptions, show_progress_bar=True)
            self._books_cache = books

            # Кэшируем жанры и авторов
            self._genres_cache = sorted(
                set(b.get('genre', '') for b in books if b.get('genre')))
            self._authors_cache = sorted(
                set(b.get('author', '') for b in books if b.get('author')))

            logger.info("Эмбеддинги вычислены")
            return self._books_cache, self._embeddings_cache

        except NoBooksFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке книг: {e}")
            raise PredictionServiceError(f"Ошибка загрузки книг: {str(e)}")

    def _filter_books(self, books: List[Dict], genre: Optional[str], author: Optional[str],
                      title: Optional[str], min_rating: float, max_year: Optional[int]) -> List[Dict]:
        filtered = []
        for book in books:
            if genre and genre != 'all' and genre != '':
                book_genre = book.get('genre', '')
                if book_genre.lower() != genre.lower():
                    continue

            if author and author != 'all' and author != '':
                book_author = book.get('author', '')
                if author.lower() not in book_author.lower():
                    continue

            if title:
                book_title = book.get('title', '')
                if title.lower() not in book_title.lower():
                    continue

            if min_rating > 0:
                book_rating = book.get('rating', 0)
                if book_rating < min_rating:
                    continue

            if max_year:
                book_year = book.get('year', 0)
                if book_year and int(book_year) > max_year:
                    continue

            filtered.append(book)

        logger.info(f"Отфильтровано {len(filtered)} книг из {len(books)}")
        return filtered

    def _format_book_response(self, book: Dict, similarity: float = 0.0) -> Dict:
        description = book.get('description', '')
        if len(description) > 300:
            description = description[:300] + '...'

        return {
            'title': book.get('title', 'Без названия'),
            'author': book.get('author', 'Автор неизвестен'),
            'year': int(book.get('year', 0)) if book.get('year') else 0,
            'genre': book.get('genre', ''),
            'rating': float(book.get('rating', 0)),
            'description': description,
            'similarity': similarity
        }

    async def predict(self, description: str, title: Optional[str] = None,
                      genre: Optional[str] = None, author: Optional[str] = None,
                      min_rating: float = 0, max_year: Optional[int] = None) -> Dict:

        try:
            books, embeddings = await self.load_books()

            if embeddings is None or len(embeddings) == 0:
                logger.error("Эмбеддинги не загружены")
                return {
                    "books": [],
                    "message": "⚠️ Сервис временно недоступен. Попробуйте позже.",
                    "count": 0
                }

            filtered_books = self._filter_books(
                books, genre, author, title, min_rating, max_year
            )

            if not filtered_books:
                logger.warning("Нет книг, соответствующих фильтрам")
                return {
                    "books": [],
                    "message": "😔 Нет книг, соответствующих выбранным фильтрам",
                    "count": 0
                }

            # Если есть описание - ищем похожие (топ 20)
            if description and description.strip():
                result = await self._search_by_description(description, filtered_books, embeddings, books)
                return result
            else:
                # Нет описания - возвращаем ВСЕ отфильтрованные книги (без ограничения 50)
                logger.info(
                    f"Поиск без описания: показано {len(filtered_books)} книг")
                formatted_books = [self._format_book_response(
                    book) for book in filtered_books]
                return {
                    "books": formatted_books,
                    "message": f"📚 Найдено {len(formatted_books)} книг по фильтрам",
                    "count": len(formatted_books)
                }

        except NoBooksFoundError as e:
            logger.error(f"Ошибка: {e}")
            return {
                "books": [],
                "message": "⚠️ База данных книг пуста. Обратитесь к администратору.",
                "count": 0
            }
        except ModelNotLoadedError as e:
            logger.error(f"Ошибка модели: {e}")
            return {
                "books": [],
                "message": "⚠️ Модель ИИ не загружена. Пожалуйста, попробуйте позже.",
                "count": 0
            }
        except Exception as e:
            logger.error(
                f"Непредвиденная ошибка при поиске: {e}", exc_info=True)
            return {
                "books": [],
                "message": "⚠️ Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.",
                "count": 0
            }

    async def _search_by_description(self, description: str, filtered_books: List[Dict],
                                     embeddings: np.ndarray, all_books: List[Dict]) -> Dict:
        logger.info(f"Поиск книг по описанию: {description[:50]}...")

        try:
            filtered_indices = []
            for filtered_book in filtered_books:
                for i, book in enumerate(all_books):
                    if book.get('id') == filtered_book.get('id'):
                        filtered_indices.append(i)
                        break

            if not filtered_indices:
                return {
                    "books": [],
                    "message": "😔 Нет книг, соответствующих фильтрам",
                    "count": 0
                }

            filtered_embeddings = embeddings[filtered_indices]
            query_embedding = self._model.encode([description])
            similarities = cosine_similarity(
                query_embedding, filtered_embeddings)[0]
            sorted_indices = np.argsort(similarities)[::-1]
            top_k = min(20, len(sorted_indices))
            top_local_indices = sorted_indices[:top_k]

            results = []
            for local_idx in top_local_indices:
                if similarities[local_idx] < 0.05:
                    continue
                book = filtered_books[local_idx]
                results.append(self._format_book_response(
                    book, float(similarities[local_idx])))

            if not results:
                return {
                    "books": [],
                    "message": "😔 Похожих книг не найдено. Попробуйте другое описание.",
                    "count": 0
                }

            logger.info(f"Найдено {len(results)} похожих книг")
            return {
                "books": results,
                "message": f"🎯 Найдено {len(results)} похожих книг",
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Ошибка при поиске по описанию: {e}")
            raise PredictionServiceError(f"Ошибка поиска: {str(e)}")

    async def get_genres(self) -> List[str]:
        try:
            await self.load_books()
            return self._genres_cache if self._genres_cache else []
        except Exception as e:
            logger.error(f"Ошибка при получении жанров: {e}")
            return []

    async def get_authors(self) -> List[str]:
        try:
            await self.load_books()
            return self._authors_cache if self._authors_cache else []
        except Exception as e:
            logger.error(f"Ошибка при получении авторов: {e}")
            return []
