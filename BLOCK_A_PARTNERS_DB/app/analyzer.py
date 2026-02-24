import re

def parse_query(text):
    """
    Извлекает регион, бюджет и тип дома из текстового запроса.
    Возвращает словарь с найденными параметрами.
    """
    result = {
        'region': None,
        'budget': None,
        'house_type': None
    }
    if not text:
        return result

    text_lower = text.lower()

    # Поиск региона
    region_patterns = [
        r'(москв[а-я]+|мск)',
        r'подмосковье|московская область|мо',
        r'ленинградская область|ленинградск|спб|питер',
        r'казань',
        r'екатеринбург',
        r'новосибирск',
        r'нижний новгород'
        # можно добавить другие
    ]
    for pattern in region_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['region'] = match.group()
            break

    # Поиск бюджета (цифры с млн/тыс/млн рублей)
    budget_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:млн|миллион|тыс|тысяч)',
        r'до\s*(\d+(?:\.\d+)?)\s*(?:млн|миллион|тыс|тысяч)',
        r'бюджет[^\d]*(\d+(?:\.\d+)?)'
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['budget'] = float(match.group(1))
            # если упоминались тысячи, переведём в млн (условно)
            if 'тыс' in match.group(0).lower():
                result['budget'] /= 1000
            break

    # Поиск типа дома
    house_types = ['каркасный', 'кирпичный', 'брус', 'газобетон', 'пеноблок', 'деревянный']
    for htype in house_types:
        if htype in text_lower:
            result['house_type'] = htype
            break

    return result
