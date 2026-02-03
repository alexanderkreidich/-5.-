import re


def validate_login(login):
    """
    Валидация логина.
    - Не пустой
    - Только латинские буквы и цифры
    - Минимум 5 символов
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not login or not login.strip():
        return False, "Поле не может быть пустым"
    
    login = login.strip()
    
    if len(login) < 5:
        return False, "Логин должен содержать минимум 5 символов"
    
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        return False, "Логин должен содержать только латинские буквы и цифры"
    
    return True, None


def validate_password(password):
    """
    Валидация пароля.
    - 8-128 символов
    - Минимум одна заглавная и одна строчная буква
    - Только латинские или кириллические буквы
    - Минимум одна цифра (арабская)
    - Без пробелов
    - Разрешённые спецсимволы: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | " ' . , : ;
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Поле не может быть пустым"
    
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    
    if len(password) > 128:
        return False, "Пароль не должен превышать 128 символов"
    
    if ' ' in password:
        return False, "Пароль не должен содержать пробелы"
    
    # Проверка на наличие заглавной буквы (латиница или кириллица)
    has_upper = bool(re.search(r'[A-ZА-ЯЁ]', password))
    if not has_upper:
        return False, "Пароль должен содержать минимум одну заглавную букву"
    
    # Проверка на наличие строчной буквы (латиница или кириллица)
    has_lower = bool(re.search(r'[a-zа-яё]', password))
    if not has_lower:
        return False, "Пароль должен содержать минимум одну строчную букву"
    
    # Проверка на наличие цифры
    has_digit = bool(re.search(r'[0-9]', password))
    if not has_digit:
        return False, "Пароль должен содержать минимум одну цифру"
    
    # Разрешённые символы: латиница, кириллица, цифры, спецсимволы
    allowed_special = r'~!?@#$%^&*_\-+\(\)\[\]{}<>/\\|"\'\.,;:'
    pattern = rf'^[a-zA-Zа-яА-ЯёЁ0-9{allowed_special}]+$'
    
    if not re.match(pattern, password):
        return False, "Пароль содержит недопустимые символы"
    
    return True, None


def validate_required_field(value, field_name):
    """
    Проверка обязательного поля.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, "Поле не может быть пустым"
    return True, None
