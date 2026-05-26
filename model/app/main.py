import sqlite3
import numpy as np
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="ML Model Service")

DB_PATH = os.environ.get('DB_PATH', '/app/data/books.db')

print("Загрузка модели SentenceTransformer...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Модель загружена!")

books_cache = None
book_embeddings_cache = None


class SearchRequest(BaseModel):
    query: str
    genre: Optional[str] = None
    author: Optional[str] = None
    min_rating: float = 0
    max_year: Optional[int] = None
    top_k: int = 20


class BookResponse(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    rating: float
    description: str
    similarity: float


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_books_and_embeddings():
    global books_cache, book_embeddings_cache

    if books_cache is not None:
        return books_cache, book_embeddings_cache

    print("Загрузка книг из базы данных...")
    conn = get_db_connection()

    # Проверяем, есть ли таблица books
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
    if not cursor.fetchone():
        raise Exception("Таблица 'books' не найдена в базе данных")

    # Загружаем все книги
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()

    print(f"Загружено {len(books)} книг")

    # Подготовка описаний для эмбеддингов
    descriptions = []
    for book in books:
        desc = book['Description'] if book['Description'] else book['Title']
        descriptions.append(str(desc))

    # Вычисление эмбеддингов
    print("Вычисление эмбеддингов для книг. Это может занять несколько минут...")
    book_embeddings_cache = model.encode(descriptions, show_progress_bar=True)
    books_cache = books
    print("Готово!")

    return books_cache, book_embeddings_cache


@app.on_event("startup")
async def startup_event():
    """При старте сервиса загружаем данные"""
    try:
        load_books_and_embeddings()
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
        raise


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": books_cache is not None}


@app.post("/search", response_model=List[BookResponse])
async def search_books(request: SearchRequest):
    """Поиск книг по текстовому запросу"""
    books, embeddings = load_books_and_embeddings()

    if len(books) == 0 or embeddings is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")

    # Определяем, есть ли текстовый запрос
    has_query = request.query and request.query.strip()

    # Фильтрация книг по метаданным
    filtered_indices = []
    for i, book in enumerate(books):
        # Фильтр по жанру
        if request.genre and request.genre != 'all':
            book_genre = book['Genre'] if book['Genre'] else ''
            if book_genre.lower() != request.genre.lower():
                continue

        # Фильтр по автору
        if request.author and request.author != 'all':
            book_author = book['Author'] if book['Author'] else ''
            if request.author.lower() not in book_author.lower():
                continue

        # Фильтр по рейтингу
        if request.min_rating > 0:
            book_rating = book['Rating'] if book['Rating'] else 0
            if float(book_rating) < request.min_rating:
                continue

        # Фильтр по году
        if request.max_year:
            book_year = book['Year'] if book['Year'] else 0
            if book_year and int(book_year) > request.max_year:
                continue

        filtered_indices.append(i)

    if len(filtered_indices) == 0:
        return []

    # Берём соответствующие эмбеддинги
    filtered_embeddings = embeddings[filtered_indices]

    # Если есть текстовый запрос - считаем похожесть
    if has_query:
        # Вычисляем эмбеддинг запроса
        query_embedding = model.encode([request.query])

        # Считаем косинусное сходство
        similarities = cosine_similarity(
            query_embedding, filtered_embeddings)[0]

        # Сортируем по убыванию сходства
        sorted_indices = np.argsort(similarities)[::-1]

        # Берем только топ (по умолчанию 20, можно настроить)
        top_k = min(request.top_k, len(filtered_indices))
        top_local_indices = sorted_indices[:top_k]
    else:
        # Нет текстового запроса - показываем ВСЕ отфильтрованные книги
        top_local_indices = list(range(len(filtered_indices)))
        # Для всех книг similarity будет 0, так как нет сравнения
        similarities = [0] * len(filtered_indices)

    # Формируем результат
    results = []
    for local_idx in top_local_indices:
        book = books[filtered_indices[local_idx]]

        description = book['Description'] if book['Description'] else ''
        if len(description) > 300:
            description = description[:300] + '...'

        results.append(BookResponse(
            title=book['Title'],
            author=book['Author'] if book['Author'] else '',
            year=int(book['Year']) if book['Year'] else 0,
            genre=book['Genre'] if book['Genre'] else '',
            rating=float(book['Rating']) if book['Rating'] else 0,
            description=description,
            similarity=float(similarities[local_idx]) if has_query else 0.0
        ))

    return results


@app.get("/genres")
async def get_genres():
    """Получить список всех жанров"""
    books, _ = load_books_and_embeddings()
    genres = set()
    for book in books:
        if book['Genre']:
            genres.add(book['Genre'])
    return sorted(list(genres))


@app.get("/authors")
async def get_authors():
    """Получить список всех авторов"""
    books, _ = load_books_and_embeddings()
    authors = set()
    for book in books:
        if book['Author']:
            authors.add(book['Author'])
    return sorted(list(authors))[:100]
