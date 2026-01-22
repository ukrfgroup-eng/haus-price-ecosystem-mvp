"""
AI-ЛОГИКА АНАЛИЗА ЗАПРОСОВ
Согласно ТЗ: AI-АНАЛИЗ ЗАПРОСОВ
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

class AIAnalyzer:
    """Анализатор запросов заказчиков с AI-логикой"""
    
    def __init__(self):
        # Ключевые слова для классификации
        self.project_keywords = {
            'строительство': [
                'строить', 'построить', 'строительство', 'дом', 'коттедж', 'дача',
                'здание', 'постройка', 'возвести', 'возведение'
            ],
            'ремонт': [
                'ремонт', 'отделка', 'ремонтировать', 'отделывать', 'косметический',
                'капитальный', 'переделка', 'обновление', 'реконструкция'
            ],
            'проектирование': [
                'проект', 'проектирование', 'план', 'чертеж', 'архитектор',
                'дизайн', 'планировка', 'эскиз', 'схема'
            ],
            'материалы': [
                'материалы', 'купить', 'продать', 'доставка', 'стройматериалы',
                'кирпич', 'доска', 'цемент', 'песок', 'инструменты'
            ]
        }
        
        self.specialization_keywords = {
            'каркасные дома': ['каркасный', 'каркас', 'деревянный', 'скелет', 'модульный'],
            'кирпичные дома': ['кирпич', 'кирпичный', 'каменный', 'блочный'],
            'отделочные работы': ['отделка', 'внутренняя', 'внутренние', 'стены', 'пол', 'потолок'],
            'кровельные работы': ['кровля', 'крыша', 'крышу', 'крыши', 'черепица'],
            'фундаменты': ['фундамент', 'основание', 'основа', 'фундамента', 'основы'],
            'электромонтаж': ['электрика', 'электромонтаж', 'проводка', 'розетки', 'свет'],
            'сантехника': ['сантехника', 'водопровод', 'канализация', 'трубы', 'унитаз'],
            'окна и двери': ['окна', 'двери', 'окон', 'дверь', 'стеклопакет'],
            'отопление и вентиляция': ['отопление', 'вентиляция', 'обогрев', 'кондиционер'],
            'ландшафтный дизайн': ['ландшафт', 'дизайн', 'участок', 'сад', 'огород']
        }
        
        # Регионы России для извлечения
        self.russian_regions = {
            'московск': 'Московская область',
            'ленинградск': 'Ленинградская область',
            'краснодарск': 'Краснодарский край',
            'свердловск': 'Свердловская область',
            'новосибирск': 'Новосибирская область',
            'татарстан': 'Республика Татарстан',
            'ростовск': 'Ростовская область',
            'челябинск': 'Челябинская область',
            'нижегородск': 'Нижегородская область',
            'самарск': 'Самарская область',
            'москв': 'Москва',
            'санкт-петербург': 'Санкт-Петербург',
            'питер': 'Санкт-Петербург',
            'сочи': 'Сочи',
            'казан': 'Казань',
            'екатеринбург': 'Екатеринбург'
        }
        
    def analyze_customer_request(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Анализ запроса заказчика"""
        message_lower = message.lower()
        
        # Извлечение сущностей
        entities = self.extract_entities(message_lower)
        
        # Классификация типа проекта
        project_type = self.classify_project_type(message_lower)
        
        # Извлечение параметров
        params = {
            'region': self.extract_region(message_lower),
            'budget_range': self.extract_budget(message_lower),
            'timeline': self.extract_timeline(message_lower),
            'urgency': self.calculate_urgency(message_lower),
            'area': self.extract_area(message_lower)
        }
        
        # Определение нужных специализаций
        specializations = self.map_to_specializations(project_type, params, message_lower)
        
        # Расчет уверенности анализа
        confidence = self.calculate_confidence(entities, params)
        
        # Определение недостающей информации
        missing_info = self.determine_missing_info(params, project_type)
        
        # Формирование рекомендаций
        recommendations = self.generate_recommendations(project_type, params, specializations)
        
        return {
            'project_type': project_type,
            'parameters': params,
            'required_specializations': specializations,
            'confidence_score': confidence,
            'entities': entities,
            'next_questions': missing_info,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'message_processed': message
        }
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Извлечение сущностей из текста"""
        entities = {
            'project_types': [],
            'specializations': [],
            'materials': [],
            'features': []
        }
        
        # Извлечение типов проектов
        for project_type, keywords in self.project_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    entities['project_types'].append(project_type)
                    break
        
        # Извлечение специализаций
        for specialization, keywords in self.specialization_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    entities['specializations'].append(specialization)
                    break
        
        # Извлечение материалов (простой паттерн)
        material_patterns = [
            r'кирпич\w*', r'дерев\w*', r'бетон\w*', r'металл\w*',
            r'стекл\w*', r'пластик\w*', r'гипсокартон\w*', r'утеплитель\w*'
        ]
        
        for pattern in material_patterns:
            matches = re.findall(pattern, message)
            if matches:
                entities['materials'].extend(matches)
        
        return entities
    
    def classify_project_type(self, message: str) -> str:
        """Классификация типа проекта"""
        scores = {
            'строительство': 0,
            'ремонт': 0,
            'проектирование': 0,
            'материалы': 0,
            'консультация': 0
        }
        
        # Подсчет ключевых слов
        for project_type, keywords in self.project_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    scores[project_type] += 1
        
        # Дополнительные правила
        if '?' in message or 'как' in message or 'совет' in message:
            scores['консультация'] += 2
        
        if 'купить' in message or 'продать' in message:
            scores['материалы'] += 2
        
        # Возвращаем тип с максимальным счетом
        max_score = max(scores.values())
        if max_score == 0:
            return 'не определен'
        
        for project_type, score in scores.items():
            if score == max_score:
                return project_type
    
    def extract_region(self, message: str) -> str:
        """Извлечение региона из текста"""
        for keyword, region in self.russian_regions.items():
            if keyword in message:
                return region
        
        # Поиск по городам
        city_keywords = ['москв', 'питер', 'сочи', 'казан', 'екатеринбург']
        for city in city_keywords:
            if city in message:
                return self.russian_regions.get(city, 'Не указан')
        
        return 'Не указан'
    
    def extract_budget(self, message: str) -> Dict[str, Any]:
        """Извлечение бюджета из текста"""
        # Паттерны для поиска бюджетов
        patterns = [
            r'(\d+)\s*-\s*(\d+)\s*(млн|тыс|миллион|тысяч)',
            r'(\d+)\s*(млн|тыс|миллион|тысяч)',
            r'до\s*(\d+)\s*(млн|тыс|миллион|тысяч)',
            r'от\s*(\d+)\s*(млн|тыс|миллион|тысяч)',
            r'(\d+)\s*млн\s*руб',
            r'(\d+)\s*тыс\s*руб',
            r'(\d+)\s*миллион\w*\s*руб',
            r'(\d+)\s*тысяч\w*\s*руб'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                for match in matches:
                    if len(match) >= 2:
                        try:
                            if 'млн' in match[1].lower() or 'миллион' in match[1].lower():
                                multiplier = 1000000
                            elif 'тыс' in match[1].lower() or 'тысяч' in match[1].lower():
                                multiplier = 1000
                            else:
                                multiplier = 1
                            
                            if len(match) >= 3:  # Диапазон
                                min_val = float(match[0]) * multiplier
                                max_val = float(match[1]) * multiplier
                                return {
                                    'min': min_val,
                                    'max': max_val,
                                    'currency': 'RUB',
                                    'source': 'range',
                                    'text': f"{match[0]}-{match[1]} {match[2]}"
                                }
                            else:  # Одно значение
                                value = float(match[0]) * multiplier
                                return {
                                    'min': value * 0.8,  # ±20%
                                    'max': value * 1.2,
                                    'currency': 'RUB',
                                    'source': 'single',
                                    'text': f"{match[0]} {match[1]}"
                                }
                        except (ValueError, IndexError):
                            continue
        
        # Если не нашли точный бюджет, определяем по категориям
        budget_keywords = {
            'эконом': {'min': 500000, 'max': 2000000},
            'средний': {'min': 2000000, 'max': 5000000},
            'премиум': {'min': 5000000, 'max': 15000000},
            'люкс': {'min': 15000000, 'max': 50000000}
        }
        
        for category, range_vals in budget_keywords.items():
            if category in message:
                return {
                    'min': range_vals['min'],
                    'max': range_vals['max'],
                    'currency': 'RUB',
                    'source': 'category',
                    'category': category
                }
        
        return {
            'min': 0,
            'max': 0,
            'currency': 'RUB',
            'source': 'not_found'
        }
    
    def extract_timeline(self, message: str) -> str:
        """Извлечение сроков из текста"""
        timeline_keywords = {
            'срочно': ['срочно', 'быстро', 'немедленно', 'как можно скорее', 'в кратчайшие сроки'],
            'ближайшее время': ['ближайшее время', 'в этом месяце', 'в следующем месяце'],
            'планирую': ['планирую', 'думаю', 'рассматриваю', 'в планах'],
            'будущее': ['в будущем', 'позже', 'не срочно', 'когда-нибудь']
        }
        
        for timeline_type, keywords in timeline_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return timeline_type
        
        return 'не указано'
    
    def extract_area(self, message: str) -> Dict[str, Any]:
        """Извлечение площади из текста"""
        area_patterns = [
            r'(\d+)\s*м[²2]',
            r'(\d+)\s*кв\s*м',
            r'(\d+)\s*квадратн\w*\s*метр',
            r'площадь\w*\s*(\d+)',
            r'(\d+)\s*соток',
            r'(\d+)\s*га'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    unit = 'м²'
                    
                    if 'соток' in pattern:
                        value *= 100  # 1 сотка = 100 м²
                        unit = 'соток'
                    elif 'га' in pattern:
                        value *= 10000  # 1 га = 10000 м²
                        unit = 'га'
                    
                    return {
                        'value': value,
                        'unit': unit,
                        'source': 'extracted'
                    }
                except (ValueError, IndexError):
                    continue
        
        return {'value': 0, 'unit': 'м²', 'source': 'not_found'}
    
    def calculate_urgency(self, message: str) -> int:
        """Расчет срочности (0-10)"""
        urgency_indicators = {
            'срочно': 3,
            'быстро': 2,
            'немедленно': 3,
            'скорее': 2,
            'срочный': 3,
            'неотложно': 3,
            'прямо сейчас': 4
        }
        
        urgency_score = 0
        message_lower = message.lower()
        
        for indicator, score in urgency_indicators.items():
            if indicator in message_lower:
                urgency_score += score
        
        # Учет восклицательных знаков
        urgency_score += message.count('!') * 0.5
        
        return min(int(urgency_score), 10)
    
    def map_to_specializations(self, project_type: str, params: Dict, message: str) -> List[str]:
        """Определение нужных специализаций"""
        specializations = []
        
        # Базовые специализации по типу проекта
        if project_type == 'строительство':
            specializations.extend(['каркасные дома', 'кирпичные дома', 'фундаменты'])
        elif project_type == 'ремонт':
            specializations.extend(['отделочные работы', 'электромонтаж', 'сантехника'])
        elif project_type == 'проектирование':
            specializations.extend(['проектирование'])
        elif project_type == 'материалы':
            specializations.extend(['продажа материалов'])
        
        # Дополнительные специализации на основе текста
        for spec, keywords in self.specialization_keywords.items():
            for keyword in keywords:
                if keyword in message and spec not in specializations:
                    specializations.append(spec)
                    break
        
        # Ограничение количества специализаций
        return list(set(specializations))[:5]
    
    def calculate_confidence(self, entities: Dict, params: Dict) -> float:
        """Расчет уверенности анализа"""
        confidence = 0.0
        
        # За каждый найденный тип проекта
        if entities.get('project_types'):
            confidence += 0.2
        
        # За каждый найденный регион
        if params.get('region') != 'Не указан':
            confidence += 0.2
        
        # За найденный бюджет
        if params.get('budget_range', {}).get('source') != 'not_found':
            confidence += 0.3
        
        # За найденные специализации
        if entities.get('specializations'):
            confidence += min(len(entities['specializations']) * 0.1, 0.3)
        
        return round(min(confidence, 1.0), 2)
    
    def determine_missing_info(self, params: Dict, project_type: str) -> List[str]:
        """Определение недостающей информации"""
        missing = []
        
        if not params.get('region') or params['region'] == 'Не указан':
            missing.append('📍 В каком регионе планируете строительство?')
        
        if params.get('budget_range', {}).get('source') == 'not_found':
            missing.append('💰 Какой примерный бюджет проекта?')
        
        if params.get('timeline') == 'не указано':
            missing.append('⏱️ Какие сроки реализации проекта?')
        
        if project_type == 'не определен':
            missing.append('🏗️ Какой тип проекта вас интересует? (строительство, ремонт, проектирование)')
        
        return missing[:3]  # Ограничиваем 3 вопросами
    
    def generate_recommendations(self, project_type: str, params: Dict, specializations: List[str]) -> Dict[str, Any]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = {
            'partner_count': 0,
            'estimated_time': '1-3 дня',
            'next_steps': [],
            'tips': []
        }
        
        # Определение количества партнеров
        budget = params.get('budget_range', {})
        if budget.get('max', 0) > 5000000:
            recommendations['partner_count'] = 3
        elif budget.get('max', 0) > 2000000:
            recommendations['partner_count'] = 5
        else:
            recommendations['partner_count'] = 7
        
        # Определение сроков
        urgency = params.get('urgency', 0)
        if urgency >= 8:
            recommendations['estimated_time'] = '2-12 часов'
            recommendations['tips'].append('⚠️ Учитывая срочность, рекомендуем сразу связаться с партнерами по телефону')
        elif urgency >= 5:
            recommendations['estimated_time'] = '1 день'
        else:
            recommendations['estimated_time'] = '1-3 дня'
        
        # Рекомендации по следующему шагу
        if project_type != 'не определен':
            recommendations['next_steps'].append(f'Подбор {recommendations["partner_count"]} проверенных {project_type}')
        
        if specializations:
            recommendations['next_steps'].append(f'Фокус на специализации: {", ".join(specializations[:2])}')
        
        # Общие советы
        recommendations['tips'].append('📞 Готовьтесь к звонкам от партнеров в течение 24 часов')
        recommendations['tips'].append('📋 Имейте под рукой детали проекта для обсуждения')
        
        return recommendations
    
    def match_partners(self, analysis_result: Dict, partners: List[Dict]) -> List[Dict]:
        """Подбор партнеров на основе анализа"""
        if not partners:
            return []
        
        matched_partners = []
        
        for partner in partners:
            score = 0
            match_factors = []
            
            # Проверка региона (30%)
            region = analysis_result['parameters']['region']
            if region != 'Не указан' and region in partner.get('regions', []):
                score += 30
                match_factors.append('регион')
            
            # Проверка специализаций (40%)
            partner_specializations = set(partner.get('specializations', []))
            required_specializations = set(analysis_result['required_specializations'])
            
            common_specializations = partner_specializations.intersection(required_specializations)
            if common_specializations:
                specialization_score = min(len(common_specializations) * 10, 40)
                score += specialization_score
                match_factors.extend(list(common_specializations)[:2])
            
            # Проверка рейтинга (20%)
            partner_rating = partner.get('rating', 0)
            score += partner_rating * 4  # 5*4=20 максимум
            
            # Проверка скорости ответа (10%)
            response_rate = partner.get('response_rate', 0)
            score += response_rate * 0.1  # 100%*0.1=10 максимум
            
            # Бонус за завершенные проекты
            completed_projects = partner.get('completed_projects', 0)
            if completed_projects > 10:
                score += min(completed_projects / 10, 5)  # до +5 баллов
            
            # Добавляем партнера с оценкой
            if score > 0:
                matched_partners.append({
                    **partner,
                    'match_score': round(min(score, 100), 1),
                    'match_factors': match_factors[:3],
                    'common_specializations': list(common_specializations)[:3]
                })
        
        # Сортировка по оценке соответствия
        matched_partners.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matched_partners
