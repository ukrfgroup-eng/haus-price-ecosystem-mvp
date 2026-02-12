import re

def extract_params(message):
    """
    Извлечение параметров из текстового запроса.
    При наличии OpenAI API можно использовать, пока заглушка.
    """
    params = {}
    # Ищем бюджет (число + млн/миллион)
    budget_match = re.search(r'(\d+)\s*(?:млн|миллион)', message)
    if budget_match:
        params['budget'] = int(budget_match.group(1)) * 1000000
    # Ищем регион
    if 'московск' in message.lower():
        params['region'] = 'Московская область'
    elif 'ленинград' in message.lower():
        params['region'] = 'Ленинградская область'
    # Ищем тип дома
    if 'каркас' in message.lower():
        params['house_type'] = 'frame'
    elif 'кирпич' in message.lower():
        params['house_type'] = 'brick'
    # Ищем площадь
    area_match = re.search(r'(\d+)\s*(?:м²|кв\.м|квадрат)', message)
    if area_match:
        params['area'] = int(area_match.group(1))
    return params
