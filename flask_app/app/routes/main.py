import logging
from flask import Blueprint, render_template, request, session, flash
from .auth import login_required
import requests
import time

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


def get_genres_from_ml():
    """Получить список жанров из ML сервиса"""
    try:
        response = requests.get("http://fastapi:8000/genres", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения жанров: {e}")
    return []


def get_authors_from_ml():
    """Получить список авторов из ML сервиса"""
    try:
        response = requests.get("http://fastapi:8000/authors", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Ошибка получения авторов: {e}")
    return []


@main_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    books = []
    query = ''
    title_filter = ''
    genre_filter = ''
    author_filter = ''
    min_rating = 0
    max_year = ''

    # Получаем списки жанров и авторов из ML сервиса
    genres = get_genres_from_ml()
    authors = get_authors_from_ml()

    if request.method == 'POST':
        query = request.form.get('query', '')
        title_filter = request.form.get('title', '')
        genre_filter = request.form.get('genre', '')
        author_filter = request.form.get('author', '')

        min_rating_str = request.form.get('min_rating', '')
        try:
            min_rating = float(min_rating_str) if min_rating_str else 0
        except ValueError:
            min_rating = 0

        max_year = request.form.get('max_year', '')

        try:
            ml_url = "http://fastapi:8000"
            response = requests.post(
                f"{ml_url}/predict",
                json={
                    "user_id": session['user_id'],
                    "description": query,
                    "title": title_filter if title_filter else None,
                    "genre": genre_filter if genre_filter else None,
                    "author": author_filter if author_filter else None,
                    "min_rating": min_rating,
                    "max_year": int(max_year) if max_year else None
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                books = data.get('books', [])
                message = data.get('message', '')
                if message:
                    flash(message, 'info')
                logger.info(
                    f"Пользователь {session['username']} выполнил поиск: найдено {len(books)} книг")
            else:
                flash('Ошибка при поиске книг', 'danger')
                logger.error(f"Ошибка поиска: статус {response.status_code}")

        except requests.exceptions.ConnectionError as e:
            flash('Не удалось подключиться к ML сервису', 'danger')
            logger.error(f"Ошибка подключения к ML сервису: {e}")
        except requests.exceptions.Timeout as e:
            flash('Превышено время ожидания ответа от ML сервиса', 'danger')
            logger.error(f"Таймаут ML сервиса: {e}")
        except Exception as e:
            flash(f'Ошибка при поиске: {str(e)}', 'danger')
            logger.error(f"Ошибка поиска: {e}")

    return render_template('index.html',
                           books=books,
                           query=query,
                           title_filter=title_filter,
                           genres=genres,
                           selected_genre=genre_filter,
                           author_filter=author_filter,
                           min_rating=min_rating,
                           max_year=max_year)
