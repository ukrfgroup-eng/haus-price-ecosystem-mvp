"""
Валидаторы данных для блока партнеров
"""

import re
from typing import Tuple, Optional


def validate_inn(inn: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация ИНН
    
    Args:
        inn: ИНН для проверки
        
    Returns:
        Tuple[валиден?, сообщение об ошибке]
    """
    # Проверка длины
    if len(inn) not in (10, 12):
        return False, "ИНН должен содержать 10 или 12 цифр"
    
    # Проверка что только цифры
    if not inn.isdigit():
        return False, "ИНН должен содержать только цифры"
    
    # Проверка контрольной суммы для 10-значного ИНН (юр.лица)
    if len(inn) == 10:
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        checksum = sum(int(inn[i]) * weights[i] for i in range(9))
        control = checksum % 11 % 10
        if control != int(inn[9]):
            return False, "Неверная контрольная сумма ИНН"
    
    # Проверка контрольной суммы для 12-значного ИНН (ИП)
    elif len(inn) == 12:
        weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
        weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 0]
        
        checksum1 = sum(int(inn[i]) * weights1[i] for i in range(11))
        control1 = checksum1 % 11 % 10
        
        checksum2 = sum(int(inn[i]) * weights2[i] for i in range(12))
        control2 = checksum2 % 11 % 10
        
        if control1 != int(inn[10]) or control2 != int(inn[11]):
            return False, "Неверная контрольная сумма ИНН"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация номера телефона
    
    Args:
        phone: Номер телефона
        
    Returns:
        Tuple[валиден?, сообщение об ошибке]
    """
    # Убираем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Проверка длины
    if len(digits) not in (10, 11):
        return False, "Номер телефона должен содержать 10-11 цифр"
    
    # Проверка кода оператора (пример)
    if digits.startswith('9') and len(digits) == 10:
        # Российские номера 9XXXXXXXXX
        return True, None
    elif digits.startswith('79') and len(digits) == 11:
        # Российские номера +79XXXXXXXXX
        return True, None
    elif digits.startswith('89') and len(digits) == 11:
        # Российские номера 89XXXXXXXXX
        return True, None
    
    return False, "Неверный формат номера телефона"


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация email адреса
    
    Args:
        email: Email для проверки
        
    Returns:
        Tuple[валиден?, сообщение об ошибке]
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, None
    else:
        return False, "Неверный формат email адреса"


def validate_ogrn(ogrn: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация ОГРН/ОГРНИП
    
    Args:
        ogrn: ОГРН для проверки
        
    Returns:
        Tuple[валиден?, сообщение об ошибке]
    """
    # ОГРН - 13 цифр, ОГРНИП - 15 цифр
    if len(ogrn) not in (13, 15):
        return False, "ОГРН должен содержать 13 цифр, ОГРНИП - 15 цифр"
    
    if not ogrn.isdigit():
        return False, "ОГРН должен содержать только цифры"
    
    # Проверка контрольной суммы
    if len(ogrn) == 13:
        # ОГРН
        checksum = int(ogrn[:12]) % 11
        control = checksum % 10 if checksum != 10 else 0
        if control != int(ogrn[12]):
            return False, "Неверная контрольная сумма ОГРН"
    else:
        # ОГРНИП
        checksum = int(ogrn[:14]) % 13
        control = checksum % 10 if checksum != 10 else 0
        if control != int(ogrn[14]):
            return False, "Неверная контрольная сумма ОГРНИП"
    
    return True, None


def validate_company_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Валидация названия компании
    
    Args:
        name: Название компании
        
    Returns:
        Tuple[валиден?, сообщение об ошибке]
    """
    if not name or not name.strip():
        return False, "Название компании не может быть пустым"
    
    if len(name.strip()) < 2:
        return False, "Название компании слишком короткое"
    
    if len(name) > 200:
        return False, "Название компании слишком длинное (макс. 200 символов)"
    
    return True, None
