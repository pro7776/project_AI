import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# URL ML-сервиса
ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://model:8002')


@app.route('/', methods=['GET', 'POST'])
def index():
    books = []
    query = ''
    genre_filter = 'all'
    author_filter = 'all'
    min_rating = 0
    max_year = ''

    # Статичные списки для фильтров (можно потом загружать из ML)
    genres = ['all', 'russian literature', 'dostoevsky',
              'tolstoy', 'chekhov', 'gogol', 'pushkin', 'turgenev']
    authors = ['all', 'Fyodor Dostoevsky', 'Leo Tolstoy', 'Anton Chekhov',
               'Nikolai Gogol', 'Alexander Pushkin', 'Ivan Turgenev']

    if request.method == 'POST':
        query = request.form.get('query', '')
        genre_filter = request.form.get('genre', 'all')
        author_filter = request.form.get('author', 'all')
        min_rating = float(request.form.get('min_rating', 0))
        max_year = request.form.get('max_year', '')

        if query.strip():
            try:
                # Запрос к ML-сервису
                response = requests.post(
                    f"{ML_SERVICE_URL}/search",
                    json={
                        "query": query,
                        "genre": genre_filter if genre_filter != 'all' else None,
                        "author": author_filter if author_filter != 'all' else None,
                        "min_rating": min_rating,
                        "max_year": int(max_year) if max_year else None,
                        "top_k": 20
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    books = response.json()
            except Exception as e:
                print(f"Ошибка при обращении к ML-сервису: {e}")

    return render_template('index.html',
                           books=books,
                           query=query,
                           genres=genres,
                           authors=authors,
                           selected_genre=genre_filter,
                           selected_author=author_filter,
                           min_rating=min_rating,
                           max_year=max_year)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
