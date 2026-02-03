from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, Role
from validators import validate_login, validate_password, validate_required_field
from decorators import check_rights

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
def index():
    """Главная страница со списком пользователей."""
    users = User.query.order_by(User.id).all()
    return render_template('index.html', users=users)


@users_bp.route('/users/<int:user_id>')
@check_rights('view_user', get_user_id=lambda kwargs: kwargs.get('user_id'))
def view(user_id):
    """Просмотр пользователя."""
    user = User.query.get_or_404(user_id)
    return render_template('user_view.html', user=user)


@users_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_user')
def create():
    """Создание нового пользователя (только Администратор)."""
    roles = Role.query.all()
    errors = {}
    form_data = {}
    
    if request.method == 'POST':
        form_data = {
            'login': request.form.get('login', '').strip(),
            'password': request.form.get('password', ''),
            'last_name': request.form.get('last_name', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'patronymic': request.form.get('patronymic', '').strip(),
            'role_id': request.form.get('role_id', '')
        }
        
        # Валидация логина
        is_valid, error = validate_login(form_data['login'])
        if not is_valid:
            errors['login'] = error
        elif User.query.filter_by(login=form_data['login']).first():
            errors['login'] = 'Пользователь с таким логином уже существует'
        
        # Валидация пароля
        is_valid, error = validate_password(form_data['password'])
        if not is_valid:
            errors['password'] = error
        
        # Валидация имени (обязательное)
        is_valid, error = validate_required_field(form_data['first_name'], 'Имя')
        if not is_valid:
            errors['first_name'] = error
        
        if not errors:
            try:
                user = User(
                    login=form_data['login'],
                    first_name=form_data['first_name'],
                    last_name=form_data['last_name'] or None,
                    patronymic=form_data['patronymic'] or None,
                    role_id=int(form_data['role_id']) if form_data['role_id'] else None
                )
                user.set_password(form_data['password'])
                db.session.add(user)
                db.session.commit()
                flash('Пользователь успешно создан', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')
    
    return render_template('user_form.html', 
                          mode='create', 
                          roles=roles, 
                          errors=errors, 
                          form_data=form_data)


@users_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights('edit_user', get_user_id=lambda kwargs: kwargs.get('user_id'))
def edit(user_id):
    """Редактирование пользователя."""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    errors = {}
    
    # Определяем, может ли пользователь менять роль
    is_admin = current_user.role and current_user.role.name == 'Администратор'
    can_change_role = is_admin
    
    if request.method == 'POST':
        form_data = {
            'last_name': request.form.get('last_name', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'patronymic': request.form.get('patronymic', '').strip(),
        }
        
        # Роль может менять только администратор
        if can_change_role:
            form_data['role_id'] = request.form.get('role_id', '')
        
        # Валидация имени (обязательное)
        is_valid, error = validate_required_field(form_data['first_name'], 'Имя')
        if not is_valid:
            errors['first_name'] = error
        
        if not errors:
            try:
                user.first_name = form_data['first_name']
                user.last_name = form_data['last_name'] or None
                user.patronymic = form_data['patronymic'] or None
                
                if can_change_role:
                    user.role_id = int(form_data['role_id']) if form_data.get('role_id') else None
                
                db.session.commit()
                flash('Пользователь успешно обновлён', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обновлении пользователя: {str(e)}', 'danger')
        
        # При ошибке сохраняем введённые данные
        user.first_name = form_data['first_name']
        user.last_name = form_data['last_name']
        user.patronymic = form_data['patronymic']
    
    return render_template('user_form.html', 
                          mode='edit', 
                          user=user, 
                          roles=roles, 
                          errors=errors,
                          can_change_role=can_change_role)


@users_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_user')
def delete(user_id):
    """Удаление пользователя (только Администратор)."""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
    
    return redirect(url_for('users.index'))
