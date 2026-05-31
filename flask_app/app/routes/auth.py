import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt

from .. import db
from ..models import User

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ============ Декораторы ============

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'administrator':
            flash('Доступ запрещён. Требуются права администратора', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ============ Маршруты ============

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.session.query(User).filter(User.username == username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role if user.role else 'user'
            logger.info(f"Пользователь {username} вошёл в систему")
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            logger.warning(f"Неудачная попытка входа: {username}")
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Заполните все поля', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')

        if len(password) < 4:
            flash('Пароль должен быть не менее 4 символов', 'danger')
            return render_template('register.html')

        existing = db.session.query(User).filter(
            User.username == username).first()
        if existing:
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(
            username=username,
            hashed_password=hashed.decode('utf-8'),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"Зарегистрирован новый пользователь: {username}")
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    logger.info(f"Пользователь {session.get('username')} вышел из системы")
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))
