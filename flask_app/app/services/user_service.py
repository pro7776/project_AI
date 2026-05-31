import logging
from sqlalchemy.orm import Session
from ..database import db
from ..models import User

logger = logging.getLogger(__name__)


def get_all_users():
    """Получить всех пользователей"""
    with Session(db.engine) as session:
        users = session.query(User).all()
        return users


def delete_user(user_id):
    """Удалить пользователя"""
    with Session(db.engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"Пользователь {user.username} удалён")
            return True
    return False


def update_user_role(user_id, new_role):
    """Изменить роль пользователя (если есть поле role)"""
    # TODO: добавить поле role в модель User
    logger.info(f"Обновление роли пользователя {user_id} на {new_role}")
    pass
