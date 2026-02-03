from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


# Права доступа по ролям
PERMISSIONS = {
    'Администратор': {
        'create_user': True,
        'edit_user': True,  # любого пользователя
        'view_user': True,  # любого пользователя
        'delete_user': True,
        'view_all_logs': True,
    },
    'Пользователь': {
        'edit_self': True,
        'view_self': True,
        'view_own_logs': True,
    }
}


def check_rights(action, get_user_id=None):
    """
    Декоратор для проверки прав пользователя.
    
    Args:
        action: Действие для проверки (например, 'edit_user', 'view_user')
        get_user_id: Функция для получения ID пользователя из аргументов view function
                     Используется для проверки, редактирует ли пользователь себя
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для доступа к данной странице необходимо войти в систему.', 'warning')
                return redirect(url_for('auth.login'))
            
            role_name = current_user.role.name if current_user.role else None
            
            if role_name == 'Администратор':
                # Администратор имеет все права
                return f(*args, **kwargs)
            
            if role_name == 'Пользователь':
                # Проверяем права обычного пользователя
                if action in ['view_user', 'edit_user']:
                    # Пользователь может только смотреть/редактировать себя
                    if get_user_id:
                        target_user_id = get_user_id(kwargs)
                        if target_user_id == current_user.id:
                            return f(*args, **kwargs)
                elif action == 'view_logs':
                    # Пользователь может смотреть только свои логи
                    return f(*args, **kwargs)
            
            flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
            return redirect(url_for('users.index'))
        
        return decorated_function
    return decorator


def can_user_do(action, target_user_id=None):
    """
    Проверка, может ли текущий пользователь выполнить действие.
    Используется в шаблонах для показа/скрытия кнопок.
    """
    if not current_user.is_authenticated:
        return False
    
    role_name = current_user.role.name if current_user.role else None
    
    if role_name == 'Администратор':
        return True
    
    if role_name == 'Пользователь':
        if action in ['view_user', 'edit_user'] and target_user_id == current_user.id:
            return True
        if action == 'view_logs':
            return True
    
    return False
