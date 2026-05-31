from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os


db = SQLAlchemy()
csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    # Инициализация расширений с приложением
    db.init_app(app)
    csrf.init_app(app)

    # Импортируем модели после инициализации db
    from .models import User, Prediction, Book

    # Создаём таблицы (только для разработки)
    with app.app_context():
        db.create_all()

    # Регистрация blueprint'ов
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.history import history_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
