from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from validators import validate_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        
        if not login_value or not password:
            flash('Заполните все поля', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(login=login_value).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно вошли в систему', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('users.index'))
        
        flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('users.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Смена пароля текущего пользователя."""
    errors = {}
    
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Проверка старого пароля
        if not current_user.check_password(old_password):
            errors['old_password'] = 'Неверный текущий пароль'
        
        # Валидация нового пароля
        is_valid, error = validate_password(new_password)
        if not is_valid:
            errors['new_password'] = error
        
        # Проверка совпадения паролей
        if new_password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
        
        if not errors:
            try:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Пароль успешно изменён', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при смене пароля: {str(e)}', 'danger')
    
    return render_template('change_password.html', errors=errors)
