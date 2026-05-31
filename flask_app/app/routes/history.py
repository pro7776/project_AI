import logging
from flask import Blueprint, render_template, session, flash
from .. import db
from ..models import Prediction
from .auth import login_required

logger = logging.getLogger(__name__)
history_bp = Blueprint('history', __name__, url_prefix='/history')


@history_bp.route('/')
@login_required
def history():
    try:
        predictions = db.session.query(Prediction).filter(
            Prediction.user_id == session['user_id']
        ).order_by(Prediction.created_at.desc()).limit(50).all()

        # Преобразуем данные для шаблона
        for pred in predictions:
            if pred.created_at:
                pred.created_at_str = pred.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S')
            else:
                pred.created_at_str = ''

            # Получаем описание из input_data
            if pred.input_data and isinstance(pred.input_data, dict):
                pred.description_preview = pred.input_data.get('description', '')[
                    :100]
            else:
                pred.description_preview = ''

        logger.info(
            f"Пользователь {session['username']} просмотрел историю ({len(predictions)} записей)")
        return render_template('history.html', predictions=predictions)
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        flash('Ошибка при загрузке истории', 'danger')
        return render_template('history.html', predictions=[])
