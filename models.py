from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Role(db.Model):
    """Модель роли пользователя."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    """Модель пользователя."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)  # Фамилия
    first_name = db.Column(db.String(100), nullable=False)  # Имя
    patronymic = db.Column(db.String(100), nullable=True)  # Отчество
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def set_password(self, password):
        """Установить хеш пароля."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Получить полное ФИО."""
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        parts.append(self.first_name)
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts)
    
    def __repr__(self):
        return f'<User {self.login}>'


class VisitLog(db.Model):
    """Журнал посещений страниц."""
    __tablename__ = 'visit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref='visits')
    
    def __repr__(self):
        return f'<VisitLog {self.path}>'
