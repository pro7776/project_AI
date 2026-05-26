import sqlite3
import bcrypt
import os
from functools import wraps
from flask import session, redirect, url_for, flash

LOGIN_DB_PATH = os.environ.get('LOGIN_DB_PATH', '/app/data/login.db')


def get_db_connection():
    conn = sqlite3.connect(LOGIN_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_login_db():
    """Инициализация базы данных пользователей (если нет таблицы)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            system TEXT NOT NULL CHECK(system IN ('users', 'administrator'))
        )
    ''')

    # Проверяем, есть ли уже администратор
    cursor.execute("SELECT * FROM all_login WHERE system = 'administrator'")
    if not cursor.fetchone():
        print("ВНИМАНИЕ: Нет администратора в базе! Создайте его через скрипт hash_password.py")

    conn.commit()
    conn.close()


def check_user(login, password):
    """Проверка логина и пароля"""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM all_login WHERE login = ?",
        (login,)
    ).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return {
            'id': user['id'],
            'login': user['login'],
            'role': user['system']
        }
    return None


def login_required(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'administrator':
            flash('Доступ запрещён. Требуются права администратора', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def register_user(login, password):
    """Регистрация нового пользователя (обычный пользователь)"""
    conn = get_db_connection()

    # Проверяем, существует ли пользователь
    existing = conn.execute(
        "SELECT * FROM all_login WHERE login = ?", (login,)).fetchone()
    if existing:
        conn.close()
        return False, "Пользователь с таким логином уже существует"

    # Хешируем пароль
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Добавляем нового пользователя (по умолчанию system = 'users')
    conn.execute(
        "INSERT INTO all_login (login, password, system) VALUES (?, ?, ?)",
        (login, hashed.decode('utf-8'), 'users')
    )
    conn.commit()
    conn.close()

    return True, "Регистрация успешна"


def update_user_info(user_id, new_login=None, new_password=None):
    """Обновление информации о пользователе"""
    conn = get_db_connection()

    if new_login:
        # Проверяем, не занят ли новый логин
        existing = conn.execute("SELECT * FROM all_login WHERE login = ? AND id != ?",
                                (new_login, user_id)).fetchone()
        if existing:
            conn.close()
            return False, "Логин уже занят"

        conn.execute("UPDATE all_login SET login = ? WHERE id = ?",
                     (new_login, user_id))

    if new_password:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        conn.execute("UPDATE all_login SET password = ? WHERE id = ?",
                     (hashed.decode('utf-8'), user_id))

    conn.commit()
    conn.close()
    return True, "Данные обновлены"


def get_user_by_id(user_id):
    """Получить пользователя по ID"""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, login, system FROM all_login WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def get_user_by_login(login):
    """Получить пользователя по логину"""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, login, system FROM all_login WHERE login = ?", (login,)).fetchone()
    conn.close()
    return user
