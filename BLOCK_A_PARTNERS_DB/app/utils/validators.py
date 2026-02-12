import re

def validate_inn(inn):
    """Проверка ИНН (10 или 12 цифр)"""
    return inn.isdigit() and len(inn) in (10, 12)

def validate_email(email):
    """Простая проверка email"""
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Проверка телефона (минимум 10 цифр)"""
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10
