import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .auth import admin_required
from .. import db
from ..models import User
from ..services.book_service import get_all_books, get_book_by_id, add_book, update_book, delete_book
import bcrypt

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def admin_panel():
    """Главная админ-панели"""
    try:
        books = get_all_books()
        users = db.session.query(User).all()
        return render_template('admin.html', books=books, users=users)
    except Exception as e:
        logger.error(f"Ошибка в админ-панели: {e}")
        flash('Ошибка загрузки админ-панели', 'danger')
        return redirect(url_for('main.index'))


@admin_bp.route('/book/add', methods=['GET', 'POST'])
@admin_required
def add_book_route():
    if request.method == 'POST':
        try:
            add_book(
                title=request.form['title'],
                author=request.form.get('author', ''),
                year=float(request.form['year']) if request.form.get(
                    'year') else None,
                genre=request.form.get('genre', ''),
                description=request.form.get('description', ''),
                rating=float(request.form.get('rating', 0)),
                rating_count=int(request.form.get('rating_count', 0))
            )
            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('admin.admin_panel'))
        except Exception as e:
            logger.error(f"Ошибка при добавлении книги: {e}")
            flash('Ошибка при добавлении книги', 'danger')

    return render_template('edit_book.html', book=None, title="Добавить книгу")


@admin_bp.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book_route(book_id):
    try:
        book = get_book_by_id(book_id)
    except Exception:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('admin.admin_panel'))

    if request.method == 'POST':
        try:
            update_book(
                book_id=book_id,
                title=request.form['title'],
                author=request.form.get('author', ''),
                year=float(request.form['year']) if request.form.get(
                    'year') else None,
                genre=request.form.get('genre', ''),
                description=request.form.get('description', ''),
                rating=float(request.form.get('rating', 0)),
                rating_count=int(request.form.get('rating_count', 0))
            )
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('admin.admin_panel'))
        except Exception as e:
            logger.error(f"Ошибка при обновлении книги: {e}")
            flash('Ошибка при обновлении книги', 'danger')

    return render_template('edit_book.html', book=book, title="Редактировать книгу")


@admin_bp.route('/book/delete/<int:book_id>')
@admin_required
def delete_book_route(book_id):
    try:
        delete_book(book_id)
        flash('Книга успешно удалена!', 'success')
    except Exception as e:
        logger.error(f"Ошибка при удалении книги: {e}")
        flash('Ошибка при удалении книги', 'danger')

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/user/make_admin/<int:user_id>')
@admin_required
def make_admin(user_id):
    if user_id == session.get('user_id'):
        flash('Нельзя изменить свою роль', 'danger')
        return redirect(url_for('admin.admin_panel'))

    try:
        user = db.session.query(User).filter(User.id == user_id).first()
        if user:
            user.role = 'administrator'
            db.session.commit()
            flash(
                f'Пользователь {user.username} назначен администратором!', 'success')
    except Exception as e:
        logger.error(f"Ошибка при назначении администратора: {e}")
        flash('Ошибка при назначении администратора', 'danger')

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/user/delete/<int:user_id>')
@admin_required
def delete_user_route(user_id):
    if user_id == session.get('user_id'):
        flash('Нельзя удалить самого себя!', 'danger')
        return redirect(url_for('admin.admin_panel'))

    try:
        user = db.session.query(User).filter(User.id == user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f'Пользователь {user.username} удалён!', 'success')
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        flash('Ошибка при удалении пользователя', 'danger')

    return redirect(url_for('admin.admin_panel'))
