
"""
Сервис поиска и фильтрации партнеров
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchService:
    """Сервис для поиска партнеров по критериям"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.cache = {}  # Простой кэш в памяти
        
    def search(
        self, 
        filters: Dict[str, Any],
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Поиск партнеров по фильтрам
        
        Args:
            filters: Словарь с фильтрами
            page: Номер страницы (начиная с 1)
            page_size: Количество результатов на странице
            
        Returns:
            Словарь с результатами поиска
        """
        try:
            # Проверяем кэш
            cache_key = self._generate_cache_key(filters, page, page_size)
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.utcnow() - cached['timestamp'] < timedelta(minutes=5):
                    logger.debug("Возвращаем результат из кэша")
                    return cached['data']
            
            # Заглушка - имитация поиска в БД
            # В реальности здесь будет запрос к базе данных
            
            # Фильтруем тестовые данные
            all_partners = self._get_test_partners()
            filtered_partners = self._apply_filters(all_partners, filters)
            
            # Сортировка
            sorted_partners = self._sort_results(filtered_partners, filters)
            
            # Пагинация
            total = len(sorted_partners)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_partners = sorted_partners[start_idx:end_idx]
            
            # Формируем ответ
            result = {
                "partners": [self._format_partner(p) for p in paginated_partners],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size,
                    "has_next": end_idx < total,
                    "has_prev": page > 1
                },
                "filters_applied": filters
            }
            
            # Сохраняем в кэш
            self.cache[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {str(e)}")
            return {
                "partners": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "total_pages": 0
                },
                "error": str(e)
            }
    
    def search_by_location(
        self, 
        city: str, 
        radius_km: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск партнеров по местоположению
        
        Args:
            city: Город для поиска
            radius_km: Радиус поиска в км (опционально)
            
        Returns:
            Список партнеров
        """
        # Заглушка - в реальности геопоиск
        filters = {"city": city}
        if radius_km:
            filters["radius_km"] = radius_km
            
        result = self.search(filters, page_size=100)
        return result["partners"]
    
    def search_by_service(
        self, 
        service_name: str, 
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск партнеров по услуге и цене
        
        Args:
            service_name: Название услуги
            max_price: Максимальная цена (опционально)
            
        Returns:
            Список партнеров
        """
        filters = {"service_name": service_name}
        if max_price:
            filters["max_price"] = max_price
            
        result = self.search(filters, page_size=100)
        return result["partners"]
    
    def get_similar_partners(self, partner_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск похожих партнеров
        
        Args:
            partner_id: ID партнера для поиска похожих
            limit: Максимальное количество результатов
            
        Returns:
            Список похожих партнеров
        """
        # Заглушка - в реальности сложная логика
        # Сейчас возвращаем случайных партнеров
        all_partners = self._get_test_partners()
        import random
        similar = random.sample(all_partners, min(limit, len(all_partners)))
        return [self._format_partner(p) for p in similar]
    
    def _apply_filters(
        self, 
        partners: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Применение фильтров к списку партнеров"""
        filtered = partners
        
        # Фильтр по городу
        if 'city' in filters and filters['city']:
            city = filters['city'].lower()
            filtered = [p for p in filtered if city in p.get('city', '').lower()]
        
        # Фильтр по региону
        if 'region' in filters and filters['region']:
            region = filters['region']
            filtered = [p for p in filtered if region in p.get('regions', [])]
        
        # Фильтр по специализации
        if 'specialization' in filters and filters['specialization']:
            spec = filters['specialization'].lower()
            filtered = [
                p for p in filtered 
                if spec in [s.lower() for s in p.get('specializations', [])]
            ]
        
        # Фильтр по услуге
        if 'service_name' in filters and filters['service_name']:
            service = filters['service_name'].lower()
            filtered = [
                p for p in filtered 
                if service in [s.get('name', '').lower() for s in p.get('services', [])]
            ]
        
        # Фильтр по минимальному рейтингу
        if 'min_rating' in filters:
            min_rating = float(filters['min_rating'])
            filtered = [p for p in filtered if p.get('rating', 0) >= min_rating]
        
        # Фильтр по статусу верификации
        if filters.get('verification_required', True):
            filtered = [p for p in filtered if p.get('verification_status') == 'verified']
        
        # Фильтр по количеству завершенных проектов
        if 'min_completed_projects' in filters:
            min_projects = int(filters['min_completed_projects'])
            filtered = [
                p for p in filtered 
                if p.get('completed_projects', 0) >= min_projects
            ]
        
        return filtered
    
    def _sort_results(
        self, 
        partners: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Сортировка результатов"""
        sort_by = filters.get('sort_by', 'rating')
        sort_order = filters.get('sort_order', 'desc')
        
        reverse = sort_order == 'desc'
        
        if sort_by == 'rating':
            return sorted(partners, key=lambda x: x.get('rating', 0), reverse=reverse)
        elif sort_by == 'price':
            # Сортировка по минимальной цене первой услуги
            def get_min_price(partner):
                services = partner.get('services', [])
                if services:
                    return min(s.get('price_min', 0) for s in services)
                return 0
            return sorted(partners, key=get_min_price, reverse=not reverse)
        elif sort_by == 'reviews':
            return sorted(
                partners, 
                key=lambda x: x.get('reviews_count', 0), 
                reverse=reverse
            )
        elif sort_by == 'response_time':
            return sorted(
                partners, 
                key=lambda x: x.get('response_time_avg', 999) or 999, 
                reverse=not reverse
            )
        else:
            return partners
    
    def _generate_cache_key(
        self, 
        filters: Dict[str, Any], 
        page: int, 
        page_size: int
    ) -> str:
        """Генерация ключа для кэша"""
        import json
        key_data = {
            'filters': filters,
            'page': page,
            'page_size': page_size
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _get_test_partners(self) -> List[Dict[str, Any]]:
        """Тестовые данные партнеров для демонстрации"""
        return [
            {
                'id': 'PART-001',
                'company_name': 'ООО СтройМастер',
                'city': 'Москва',
                'regions': ['77'],
                'specializations': ['Ремонт', 'Строительство'],
                'services': [
                    {'name': 'Ремонт квартир', 'price_min': 1000, 'price_max': 5000},
                    {'name': 'Строительство домов', 'price_min': 5000, 'price_max': 20000}
                ],
                'rating': 4.5,
                'reviews_count': 42,
                'completed_projects': 35,
                'verification_status': 'verified',
                'response_time_avg': 2.5
            },
            {
                'id': 'PART-002',
                'company_name': 'ИП Иванов Сантехник',
                'city': 'Москва',
                'regions': ['77', '50'],
                'specializations': ['Сантехника', 'Отопление'],
                'services': [
                    {'name': 'Установка сантехники', 'price_min': 500, 'price_max': 3000},
                    {'name': 'Ремонт отопления', 'price_min': 1000, 'price_max': 8000}
                ],
                'rating': 4.2,
                'reviews_count': 28,
                'completed_projects': 22,
                'verification_status': 'verified',
                'response_time_avg': 1.8
            },
            {
                'id': 'PART-003',
                'company_name': 'ООО Электрик Профи',
                'city': 'Санкт-Петербург',
                'regions': ['78'],
                'specializations': ['Электрика', 'Умный дом'],
                'services': [
                    {'name': 'Электромонтажные работы', 'price_min': 800, 'price_max': 4000},
                    {'name': 'Установка умного дома', 'price_min': 5000, 'price_max': 25000}
                ],
                'rating': 4.7,
                'reviews_count': 56,
                'completed_projects': 48,
                'verification_status': 'pending',
                'response_time_avg': 3.2
            },
            {
                'id': 'PART-004',
                'company_name': 'ООО Отделочные работы',
                'city': 'Москва',
                'regions': ['77'],
                'specializations': ['Отделка', 'Дизайн'],
                'services': [
                    {'name': 'Отделка стен', 'price_min': 300, 'price_max': 1500},
                    {'name': 'Дизайн интерьера', 'price_min': 5000, 'price_max': 30000}
                ],
                'rating': 4.0,
                'reviews_count': 19,
                'completed_projects': 15,
                'verification_status': 'verified',
                'response_time_avg': 4.5
            }
        ]
    
    def _format_partner(self, partner: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование партнера для ответа API"""
        return {
            'id': partner['id'],
            'company_name': partner['company_name'],
            'city': partner['city'],
            'specializations': partner['specializations'],
            'rating': partner['rating'],
            'reviews_count': partner['reviews_count'],
            'completed_projects': partner['completed_projects'],
            'verification_status': partner['verification_status'],
            'response_time_hours': partner.get('response_time_avg'),
            'services': [
                {
                    'name': s['name'],
                    'price_range': f"{s['price_min']} - {s['price_max']} руб."
                }
                for s in partner['services'][:3]  # Первые 3 услуги
            ]
        }
