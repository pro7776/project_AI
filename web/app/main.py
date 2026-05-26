
import requests
from flask import Flask, render_template, request, session, redirect, url_for, flash
from auth import check_user, login_required, admin_required, init_login_db, update_user_info, get_user_by_id
from admin import (
    get_all_books, get_book_by_id, add_book, update_book, delete_book,
    get_all_users, add_user, delete_user, update_user_role, update_user_by_admin
)
import bcrypt
import sys
import os


app = Flask(__name__)
app.secret_key = os.environ.get(
    'SECRET_KEY', 'your-secret-key-here-change-in-production')

ML_SERVICE_URL = os.environ.get('ML_SERVICE_URL', 'http://model:8002')

# Инициализация БД пользователей при старте
init_login_db()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('login')
        password = request.form.get('password')

        user = check_user(login_val, password)
        if user:
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            session['role'] = user['role']
            flash(f'Добро пожаловать, {login_val}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    books = []
    query = ''
    title_filter = ''
    genre_filter = 'all'
    author_filter = 'all'
    min_rating = 0
    max_year = ''

    if request.method == 'POST':
        query = request.form.get('query', '')
        title_filter = request.form.get('title', '')
        genre_filter = request.form.get('genre', 'all')
        author_filter = request.form.get('author', 'all')
        min_rating = float(request.form.get('min_rating', 0))
        max_year = request.form.get('max_year', '')

        search_params = {
            "query": query if query else title_filter,
            "genre": genre_filter if genre_filter != 'all' else None,
            "author": author_filter if author_filter != 'all' else None,
            "min_rating": min_rating,
            "max_year": int(max_year) if max_year else None,
            "top_k": 50
        }

        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/search",
                json=search_params,
                timeout=60
            )
            if response.status_code == 200:
                books = response.json()
                if title_filter:
                    books = [b for b in books if title_filter.lower()
                             in b['title'].lower()]
        except Exception as e:
            flash(f'Ошибка при поиске: {e}', 'danger')

    genres = ['all']
    authors = ['all']
    try:
        resp = requests.get(f"{ML_SERVICE_URL}/genres", timeout=10)
        if resp.status_code == 200:
            genres = ['all'] + resp.json()
    except:
        pass

    try:
        resp = requests.get(f"{ML_SERVICE_URL}/authors", timeout=10)
        if resp.status_code == 200:
            authors = ['all'] + resp.json()
    except:
        pass

    return render_template('index.html',
                           books=books,
                           query=query,
                           title_filter=title_filter,
                           genres=genres,
                           authors=authors,
                           selected_genre=genre_filter,
                           selected_author=author_filter,
                           min_rating=min_rating,
                           max_year=max_year,
                           user_role=session.get('role'))

# ============ Админские маршруты ============


@app.route('/admin')
@admin_required
def admin_panel():
    books = get_all_books()
    users = get_all_users()
    return render_template('admin.html', books=books, users=users)


@app.route('/admin/book/add', methods=['GET', 'POST'])
@admin_required
def add_book_route():
    if request.method == 'POST':
        add_book(
            title=request.form['title'],
            author=request.form['author'],
            year=float(request.form['year']) if request.form['year'] else None,
            genre=request.form['genre'],
            description=request.form['description'],
            rating=float(request.form['rating']
                         ) if request.form['rating'] else 0,
            rating_count=int(
                request.form['rating_count']) if request.form['rating_count'] else 0
        )
        flash('Книга добавлена!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('edit_book.html', book=None)


@app.route('/admin/book/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book_route(book_id):
    book = get_book_by_id(book_id)

    if request.method == 'POST':
        update_book(
            book_id=book_id,
            title=request.form['title'],
            author=request.form['author'],
            year=float(request.form['year']) if request.form['year'] else None,
            genre=request.form['genre'],
            description=request.form['description'],
            rating=float(request.form['rating']
                         ) if request.form['rating'] else 0,
            rating_count=int(
                request.form['rating_count']) if request.form['rating_count'] else 0
        )
        flash('Книга обновлена!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('edit_book.html', book=book)


@app.route('/admin/book/delete/<int:book_id>')
@admin_required
def delete_book_route(book_id):
    delete_book(book_id)
    flash('Книга удалена!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user_route():
    login = request.form['login']
    password = request.form['password']
    system = request.form['system']

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if add_user(login, hashed.decode('utf-8'), system):
        flash(f'Пользователь {login} добавлен!', 'success')
    else:
        flash(f'Пользователь {login} уже существует!', 'danger')

    return redirect(url_for('admin_panel'))


@app.route('/admin/user/delete/<int:user_id>')
@admin_required
def delete_user_route(user_id):
    if user_id == session['user_id']:
        flash('Нельзя удалить самого себя!', 'danger')
    else:
        delete_user(user_id)
        flash('Пользователь удалён!', 'success')

    return redirect(url_for('admin_panel'))


@app.route('/admin/user/role/<int:user_id>/<string:new_role>')
@admin_required
def change_user_role(user_id, new_role):
    if new_role not in ['users', 'administrator']:
        flash('Некорректная роль!', 'danger')
    elif user_id == session['user_id']:
        flash('Нельзя изменить свою роль!', 'danger')
    else:
        update_user_role(user_id, new_role)
        flash(f'Роль изменена на {new_role}!', 'success')

    return redirect(url_for('admin_panel'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Проверка пароля
        if not login or not password:
            flash('Заполните все поля', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')

        if len(password) < 4:
            flash('Пароль должен быть не менее 4 символов', 'danger')
            return render_template('register.html')

        # Регистрация
        from auth import register_user
        success, message = register_user(login, password)

        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')

    return render_template('register.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Проверяем, редактирует ли админ другого пользователя
    edit_user_id = request.args.get('edit', type=int)

    # Если админ редактирует другого пользователя
    if session.get('role') == 'administrator' and edit_user_id and edit_user_id != session['user_id']:
        user = get_user_by_id(edit_user_id)
        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('admin_panel'))
        is_admin_editing = True
    else:
        user = get_user_by_id(session['user_id'])
        is_admin_editing = False

    if request.method == 'POST':
        # Проверяем, от кого пришёл запрос
        if is_admin_editing:
            # Админ редактирует другого пользователя
            new_login = request.form.get('login')
            new_password = request.form.get('password')
            new_role = request.form.get('role')

            # Обновляем через админскую функцию
            from admin import update_user_by_admin
            update_user_by_admin(
                edit_user_id, new_login, new_password if new_password else None, new_role)
            flash('Пользователь обновлён', 'success')
            return redirect(url_for('admin_panel'))
        else:
            # Пользователь редактирует себя
            new_login = request.form.get('new_login')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password and new_password != confirm_password:
                flash('Пароли не совпадают', 'danger')
                return render_template('profile.html', user=user, is_admin_editing=False)

            if new_password and len(new_password) < 4:
                flash('Пароль должен быть не менее 4 символов', 'danger')
                return render_template('profile.html', user=user, is_admin_editing=False)

            success, message = update_user_info(
                session['user_id'],
                new_login=new_login if new_login else None,
                new_password=new_password if new_password else None
            )

            if success:
                if new_login:
                    session['user_login'] = new_login
                flash(message, 'success')
                return redirect(url_for('profile'))
            else:
                flash(message, 'danger')

    return render_template('profile.html',
                           user=user,
                           is_admin_editing=is_admin_editing)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
