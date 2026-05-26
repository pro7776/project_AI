import sqlite3
import os
from flask import request, render_template, redirect, url_for, flash
from functools import wraps

BOOKS_DB_PATH = os.environ.get('DB_PATH', '/app/data/books.db')
LOGIN_DB_PATH = os.environ.get('LOGIN_DB_PATH', '/app/data/login.db')


def get_books_connection():
    conn = sqlite3.connect(BOOKS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_login_connection():
    conn = sqlite3.connect(LOGIN_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_books():
    """Получить все книги"""
    conn = get_books_connection()
    books = conn.execute('SELECT * FROM books ORDER BY id').fetchall()
    conn.close()
    return books


def get_book_by_id(book_id):
    """Получить книгу по ID"""
    conn = get_books_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?',
                        (book_id,)).fetchone()
    conn.close()
    return book


def add_book(title, author, year, genre, description, rating, rating_count):
    """Добавить новую книгу"""
    conn = get_books_connection()
    conn.execute('''
        INSERT INTO books (Title, Author, Year, Genre, Description, Rating, Rating_Count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, year, genre, description, rating, rating_count))
    conn.commit()
    conn.close()


def update_book(book_id, title, author, year, genre, description, rating, rating_count):
    """Обновить книгу"""
    conn = get_books_connection()
    conn.execute('''
        UPDATE books 
        SET Title = ?, Author = ?, Year = ?, Genre = ?, Description = ?, Rating = ?, Rating_Count = ?
        WHERE id = ?
    ''', (title, author, year, genre, description, rating, rating_count, book_id))
    conn.commit()
    conn.close()


def delete_book(book_id):
    """Удалить книгу"""
    conn = get_books_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()


def get_all_users():
    """Получить всех пользователей"""
    conn = get_login_connection()
    users = conn.execute(
        'SELECT id, login, system FROM all_login ORDER BY id').fetchall()
    conn.close()
    return users


def add_user(login, password_hash, system):
    """Добавить нового пользователя"""
    conn = get_login_connection()
    try:
        conn.execute(
            'INSERT INTO all_login (login, password, system) VALUES (?, ?, ?)',
            (login, password_hash, system)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_user(user_id):
    """Удалить пользователя"""
    conn = get_login_connection()
    conn.execute('DELETE FROM all_login WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def update_user_role(user_id, new_role):
    """Изменить роль пользователя"""
    conn = get_login_connection()
    conn.execute('UPDATE all_login SET system = ? WHERE id = ?',
                 (new_role, user_id))
    conn.commit()
    conn.close()


def update_user_by_admin(user_id, login, password=None, role=None):
    """Обновление пользователя администратором"""
    conn = get_login_connection()

    # Обновляем логин
    if login:
        conn.execute("UPDATE all_login SET login = ? WHERE id = ?",
                     (login, user_id))

    # Обновляем пароль
    if password:
        import bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn.execute("UPDATE all_login SET password = ? WHERE id = ?",
                     (hashed.decode('utf-8'), user_id))

    # Обновляем роль
    if role:
        conn.execute(
            "UPDATE all_login SET system = ? WHERE id = ?", (role, user_id))

    conn.commit()
    conn.close()
