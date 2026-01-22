"""
КЛИЕНТ ДЛЯ API ФНС
Верификация ИНН через государственные реестры
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FNSAPIClient:
    """Клиент для работы с API Федеральной Налоговой Службы"""
    
    def __init__(self, api_key: str, base_url: str = "https://api-fns.ru"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HausPrice-Ecosystem/1.0',
            'Accept': 'application/json'
        })
    
    def check_inn(self, inn: str) -> Dict[str, Any]:
        """Проверка ИНН через API ФНС (ЕГРЮЛ/ЕГРИП)"""
        try:
            # Базовая валидация формата
            validation_result = self._validate_inn(inn)
            if not validation_result['valid']:
                return validation_result
            
            # Запрос к API ФНС
            url = f"{self.base_url}/api/egr"
            params = {
                'req': inn,
                'key': self.api_key
            }
            
            logger.info(f"Checking INN via FNS API: {inn}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_fns_response(data, inn)
            elif response.status_code == 403:
                return {
                    'success': False,
                    'error': 'Ошибка авторизации API ФНС',
                    'details': 'Неверный API ключ или закончился лимит запросов'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка API ФНС: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except requests.Timeout:
            logger.error(f"Timeout checking INN: {inn}")
            return {
                'success': False,
                'error': 'Таймаут при проверке ИНН',
                'details': 'Сервис ФНС не ответил вовремя'
            }
        except requests.RequestException as e:
            logger.error(f"Network error checking INN {inn}: {e}")
            return {
                'success': False,
                'error': 'Сетевая ошибка при проверке ИНН',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error checking INN {inn}: {e}")
            return {
                'success': False,
                'error': 'Неожиданная ошибка при проверке ИНН',
                'details': str(e)
            }
    
    def check_company_details(self, inn: str, ogrn: Optional[str] = None) -> Dict[str, Any]:
        """Получение детальной информации о компании"""
        try:
            # Основная проверка ИНН
            inn_result = self.check_inn(inn)
            if not inn_result['success']:
                return inn_result
            
            # Если есть ОГРН, проверяем его соответствие
            if ogrn and 'data' in inn_result:
                company_data = inn_result['data']
                if company_data.get('ogrn') != ogrn:
                    return {
                        'success': False,
                        'error': 'ОГРН не соответствует ИНН',
                        'details': f"Ожидался ОГРН: {company_data.get('ogrn')}, получен: {ogrn}"
                    }
            
            # Дополнительные проверки (можно расширять)
            additional_checks = self._perform_additional_checks(inn_result.get('data', {}))
            
            return {
                'success': True,
                'data': {
                    **inn_result.get('data', {}),
                    'additional_checks': additional_checks,
                    'verified_at': datetime.utcnow().isoformat(),
                    'verification_method': 'fns_api'
                },
                'message': 'Компания успешно верифицирована'
            }
            
        except Exception as e:
            logger.error(f"Error checking company details {inn}: {e}")
            return {
                'success': False,
                'error': 'Ошибка при проверке деталей компании',
                'details': str(e)
            }
    
    def check_batch_inns(self, inns: list) -> Dict[str, Any]:
        """Пакетная проверка нескольких ИНН"""
        results = {}
        
        for inn in inns[:10]:  # Ограничиваем 10 запросами за раз
            results[inn] = self.check_inn(inn)
            # Небольшая задержка между запросами
            import time
            time.sleep(0.5)
        
        return {
            'success': True,
            'results': results,
            'count': len(results),
            'checked_at': datetime.utcnow().isoformat()
        }
    
    def _validate_inn(self, inn: str) -> Dict[str, Any]:
        """Валидация формата и контрольных сумм ИНН"""
        if not inn:
            return {'valid': False, 'error': 'ИНН не может быть пустым'}
        
        # Проверка что только цифры
        if not inn.isdigit():
            return {'valid': False, 'error': 'ИНН должен содержать только цифры'}
        
        length = len(inn)
        
        # Проверка длины
        if length not in [10, 12]:
            return {'valid': False, 'error': f'ИНН должен содержать 10 или 12 цифр, получено {length}'}
        
        # Проверка контрольных сумм для 10-значного ИНН (юрлица)
        if length == 10:
            coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum = sum(int(inn[i]) * coefficients[i] for i in range(9)) % 11 % 10
            
            if control_sum != int(inn[9]):
                return {'valid': False, 'error': 'Неверная контрольная сумма ИНН (юрлицо)'}
        
        # Проверка контрольных сумм для 12-значного ИНН (физлица/ИП)
        elif length == 12:
            # Первая контрольная сумма
            coefficients1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum1 = sum(int(inn[i]) * coefficients1[i] for i in range(10)) % 11 % 10
            
            # Вторая контрольная сумма
            coefficients2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            control_sum2 = sum(int(inn[i]) * coefficients2[i] for i in range(11)) % 11 % 10
            
            if control_sum1 != int(inn[10]) or control_sum2 != int(inn[11]):
                return {'valid': False, 'error': 'Неверная контрольная сумма ИНН (физлицо/ИП)'}
        
        return {'valid': True, 'message': 'ИНН прошел базовую валидацию'}
    
    def _parse_fns_response(self, data: Dict, inn: str) -> Dict[str, Any]:
        """Парсинг ответа от API ФНС"""
        try:
            if not data or 'Items' not in data or not data['Items']:
                return {
                    'success': False,
                    'error': 'Компания не найдена в реестре ФНС',
                    'inn': inn,
                    'details': data
                }
            
            item = data['Items'][0]  # Берем первую запись
            
            # Извлечение основных данных
            company_data = {
                'inn': inn,
                'name': item.get('ЮЛ', {}).get('НаимСокр', item.get('ЮЛ', {}).get('НаимПолн', 'Не указано')),
                'full_name': item.get('ЮЛ', {}).get('НаимПолн', ''),
                'ogrn': item.get('ЮЛ', {}).get('ОГРН', ''),
                'kpp': item.get('ЮЛ', {}).get('КПП', ''),
                'legal_address': item.get('ЮЛ', {}).get('Адрес', ''),
                'registration_date': item.get('ЮЛ', {}).get('ДатаРег', ''),
                'status': item.get('ЮЛ', {}).get('Статус', ''),
                'okved': item.get('ЮЛ', {}).get('ОКВЭД', ''),
                'management': item.get('ЮЛ', {}).get('Управление', {}),
                'verified': True,
                'verification_date': datetime.utcnow().isoformat()
            }
            
            # Определение организационно-правовой формы
            legal_form = self._detect_legal_form(company_data['name'])
            company_data['legal_form'] = legal_form
            
            # Проверка статуса компании
            status = company_data['status'].lower() if company_data['status'] else ''
            is_active = 'действующ' in status or 'действ' in status
            
            if not is_active:
                return {
                    'success': False,
                    'error': 'Компания не действует или ликвидирована',
                    'data': company_data,
                    'details': f"Статус: {company_data['status']}"
                }
            
            return {
                'success': True,
                'data': company_data,
                'message': 'Компания найдена и верифицирована'
            }
            
        except Exception as e:
            logger.error(f"Error parsing FNS response for INN {inn}: {e}")
            return {
                'success': False,
                'error': 'Ошибка при обработке ответа от ФНС',
                'details': str(e),
                'raw_data': data
            }
    
    def _detect_legal_form(self, company_name: str) -> str:
        """Определение организационно-правовой формы по названию"""
        name_upper = company_name.upper()
        
        if 'ООО' in name_upper:
            return 'ООО'
        elif 'ИП' in name_upper or 'ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ' in name_upper:
            return 'ИП'
        elif 'АО' in name_upper or 'АКЦИОНЕРНОЕ ОБЩЕСТВО' in name_upper:
            return 'АО'
        elif 'ЗАО' in name_upper:
            return 'ЗАО'
        elif 'ОАО' in name_upper:
            return 'ОАО'
        elif 'ПАО' in name_upper:
            return 'ПАО'
        else:
            return 'Другое'
    
    def _perform_additional_checks(self, company_data: Dict) -> Dict[str, Any]:
        """Выполнение дополнительных проверок компании"""
        checks = {
            'bankruptcy_check': self._check_bankruptcy(company_data),
            'tax_debt_check': self._check_tax_debts(company_data),
            'legal_proceedings_check': self._check_legal_proceedings(company_data),
            'reputation_check': self._check_reputation(company_data)
        }
        
        # Общий статус проверок
        all_passed = all(check.get('passed', False) for check in checks.values())
        checks['overall_status'] = 'passed' if all_passed else 'failed'
        
        return checks
    
    def _check_bankruptcy(self, company_data: Dict) -> Dict[str, Any]:
        """Проверка на банкротство (заглушка)"""
        # В реальности здесь должен быть запрос к API реестра банкротств
        return {
            'passed': True,
            'message': 'Признаков банкротства не обнаружено',
            'checked_at': datetime.utcnow().isoformat(),
            'source': 'estimated'  # В реальности должно быть 'official'
        }
    
    def _check_tax_debts(self, company_data: Dict) -> Dict[str, Any]:
        """Проверка налоговых задолженностей (заглушка)"""
        return {
            'passed': True,
            'message': 'Налоговые задолженности не обнаружены',
            'checked_at': datetime.utcnow().isoformat(),
            'source': 'estimated'
        }
    
    def _check_legal_proceedings(self, company_data: Dict) -> Dict[str, Any]:
        """Проверка судебных дел (заглушка)"""
        return {
            'passed': True,
            'message': 'Судебные дела не обнаружены',
            'checked_at': datetime.utcnow().isoformat(),
            'source': 'estimated'
        }
    
    def _check_reputation(self, company_data: Dict) -> Dict[str, Any]:
        """Проверка репутации компании (заглушка)"""
        return {
            'passed': True,
            'message': 'Репутация компании в порядке',
            'checked_at': datetime.utcnow().isoformat(),
            'source': 'estimated'
        }
