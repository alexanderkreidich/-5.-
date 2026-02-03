from flask import Flask, request
from flask_login import LoginManager, current_user
from models import db, User, Role, VisitLog
from decorators import can_user_do

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к данной странице необходимо войти в систему'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Добавляем can_user_do в контекст шаблонов
@app.context_processor
def utility_processor():
    return dict(can_user_do=can_user_do)


# Логирование посещений страниц
@app.before_request
def log_visit():
    # Не логируем статические файлы
    if request.path.startswith('/static'):
        return
    
    visit = VisitLog(
        path=request.path,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(visit)
    try:
        db.session.commit()
    except:
        db.session.rollback()


# Register blueprints
from auth import auth_bp
from users import users_bp
from reports import reports_bp

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(reports_bp)


def init_db():
    """Инициализация базы данных с тестовыми данными."""
    with app.app_context():
        db.create_all()
        
        # Создаём роли если их нет
        if not Role.query.first():
            roles = [
                Role(name='Администратор', description='Полный доступ к системе'),
                Role(name='Пользователь', description='Базовый доступ')
            ]
            for role in roles:
                db.session.add(role)
            db.session.commit()
        
        # Создаём тестового администратора если нет пользователей
        if not User.query.first():
            admin = User(
                login='admin',
                first_name='Администратор',
                last_name='Системный',
                role_id=1
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            
            # Создаём обычного пользователя для тестирования
            user = User(
                login='user1',
                first_name='Иван',
                last_name='Иванов',
                patronymic='Иванович',
                role_id=2
            )
            user.set_password('User1234!')
            db.session.add(user)
            
            db.session.commit()
            print('Созданы тестовые пользователи:')
            print('  Администратор: admin / Admin123!')
            print('  Пользователь: user1 / User1234!')


if __name__ == '__main__':
    import os
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
