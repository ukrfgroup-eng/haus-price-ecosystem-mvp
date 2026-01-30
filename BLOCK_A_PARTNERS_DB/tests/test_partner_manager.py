"""
Тесты для сервиса управления партнерами
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from ..services.partner_manager import PartnerManager
from ..services.verification_service import VerificationService
from ..models.partner_models import Partner, PartnerContact


class TestPartnerManager:
    """Тесты для PartnerManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_db = Mock()
        self.mock_verification = Mock(spec=VerificationService)
        self.manager = PartnerManager(self.mock_db, self.mock_verification)
    
    def test_generate_public_id(self):
        """Тест генерации публичного ID"""
        public_id = self.manager.generate_public_id()
        
        assert public_id.startswith("PART-")
        assert len(public_id) == 10  # PART-XXXXXX
    
    def test_register_partner_success(self):
        """Тест успешной регистрации партнера"""
        # Мокаем успешную проверку ИНН
        self.mock_verification.verify_inn.return_value = {
            "is_valid": True,
            "legal_form": "ООО",
            "ogrn": "1234567890123",
            "legal_address": "Москва, ул. Тестовая, 1"
        }
        
        contact_data = {
            "phone": "+79991234567",
            "email": "test@example.com",
            "contact_person": "Иван Иванов",
            "position": "Директор"
        }
        
        partner = self.manager.register_partner(
            legal_name="ООО Тест",
            inn="1234567890",
            contact=contact_data,
            source="bot"
        )
        
        assert partner is not None
        assert partner.legal_name == "ООО Тест"
        assert partner.inn == "1234567890"
        assert partner.verification_status.value == "pending"
        assert partner.contact.phone == "+79991234567"
        assert partner.contact.email == "test@example.com"
        assert partner.created_by == "system"
    
    def test_register_partner_invalid_inn(self):
        """Тест регистрации с невалидным ИНН"""
        # Мокаем неудачную проверку ИНН
        self.mock_verification.verify_inn.return_value = {
            "is_valid": False,
            "error": "Неверный ИНН"
        }
        
        contact_data = {
            "phone": "+79991234567",
            "email": "test@example.com",
            "contact_person": "Иван Иванов",
            "position": "Директор"
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.manager.register_partner(
                legal_name="ООО Тест",
                inn="invalid",
                contact=contact_data
            )
        
        assert "Invalid INN" in str(exc_info.value)
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    def test_update_partner_success(self, mock_get_partner):
        """Тест успешного обновления партнера"""
        # Создаем тестового партнера
        test_partner = Partner(
            id="test-id",
            public_id="PART-001",
            legal_name="ООО Старое название",
            inn="1234567890"
        )
        test_partner.contact = PartnerContact(
            phone="+79991234567",
            email="old@example.com",
            contact_person="Иван Иванов",
            position="Директор"
        )
        
        mock_get_partner.return_value = test_partner
        
        update_data = {
            "trading_name": "Новое торговое название",
            "actual_address": "Москва, новый адрес",
            "main_category": "Ремонт",
            "specializations": ["Строительство", "Отделка"]
        }
        
        updated = self.manager.update_partner("test-id", update_data)
        
        assert updated is not None
        assert updated.trading_name == "Новое торговое название"
        assert updated.actual_address == "Москва, новый адрес"
        assert updated.main_category == "Ремонт"
        assert updated.specializations == ["Строительство", "Отделка"]
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    def test_update_partner_not_found(self, mock_get_partner):
        """Тест обновления несуществующего партнера"""
        mock_get_partner.return_value = None
        
        update_data = {"trading_name": "Новое название"}
        updated = self.manager.update_partner("non-existent", update_data)
        
        assert updated is None
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    def test_add_service_success(self, mock_get_partner):
        """Тест добавления услуги партнеру"""
        test_partner = Partner(
            id="test-id",
            public_id="PART-001",
            legal_name="ООО Тест",
            inn="1234567890"
        )
        
        mock_get_partner.return_value = test_partner
        
        service_data = {
            "name": "Ремонт ванной комнаты",
            "description": "Полный ремонт ванной комнаты",
            "unit": "м²",
            "price_min": 5000,
            "price_max": 15000,
            "category": "Ремонт"
        }
        
        service = self.manager.add_service("test-id", service_data)
        
        assert service is not None
        assert service.name == "Ремонт ванной комнаты"
        assert len(test_partner.services) == 1
        assert test_partner.services[0] == service
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    def test_add_service_partner_not_found(self, mock_get_partner):
        """Тест добавления услуги несуществующему партнеру"""
        mock_get_partner.return_value = None
        
        service_data = {
            "name": "Услуга",
            "description": "Описание",
            "unit": "шт",
            "price_min": 100,
            "price_max": 200
        }
        
        service = self.manager.add_service("non-existent", service_data)
        
        assert service is None
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    @patch.object(PartnerManager, '_calculate_verification_score')
    def test_verify_partner_success(self, mock_calc_score, mock_get_partner):
        """Тест успешной верификации партнера"""
        test_partner = Partner(
            id="test-id",
            public_id="PART-001",
            legal_name="ООО Тест",
            inn="1234567890"
        )
        
        mock_get_partner.return_value = test_partner
        mock_calc_score.return_value = 85.0
        
        # Мокаем проверку документов и ФНС
        self.mock_verification.verify_documents.return_value = True
        self.mock_verification.verify_via_fns.return_value = {
            "success": True,
            "checks": {"is_active": True}
        }
        
        success = self.manager.verify_partner("test-id", admin_id="admin123")
        
        assert success is True
        assert test_partner.verification_status.value == "verified"
        assert test_partner.verification_score == 85.0
        assert test_partner.verified_by == "admin123"
        assert test_partner.is_active is True
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    @patch.object(PartnerManager, '_calculate_verification_score')
    def test_verify_partner_rejected(self, mock_calc_score, mock_get_partner):
        """Тест отклонения верификации"""
        test_partner = Partner(
            id="test-id",
            public_id="PART-001",
            legal_name="ООО Тест",
            inn="1234567890"
        )
        
        mock_get_partner.return_value = test_partner
        mock_calc_score.return_value = 65.0  # Меньше 80
        
        success = self.manager.verify_partner("test-id")
        
        assert success is False
        assert test_partner.verification_status.value == "rejected"
        assert test_partner.rejection_reason is not None
    
    @patch.object(PartnerManager, '_get_partner_by_id')
    def test_verify_partner_not_found(self, mock_get_partner):
        """Тест верификации несуществующего партнера"""
        mock_get_partner.return_value = None
        
        success = self.manager.verify_partner("non-existent")
        
        assert success is False
    
    def test_calculate_verification_score(self):
        """Тест расчета баллов верификации"""
        test_partner = Partner(
            id="test-id",
            public_id="PART-001",
            legal_name="ООО Тест",
            inn="1234567890"
        )
        
        # Тест с максимальными баллами
        test_partner.contact = PartnerContact(
            phone="+79991234567",
            email="test@example.com",
            contact_person="Иван Иванов",
            position="Директор"
        )
        test_partner.services = [Mock()]
        test_partner.regions = ["77"]
        
        score = self.manager._calculate_verification_score(
            test_partner,
            docs_verified=True,
            fns_verified=True
        )
        
        # 40 (ФНС) + 30 (документы) + 10 (телефон) + 10 (услуги) + 10 (регионы) = 100
        assert score == 100.0
        
        # Тест с минимальными баллами
        test_partner.contact = None
        test_partner.services = []
        test_partner.regions = []
        
        score = self.manager._calculate_verification_score(
            test_partner,
            docs_verified=False,
            fns_verified=False
        )
        
        assert score == 0.0


def test_partner_to_dict():
    """Тест преобразования партнера в словарь"""
    partner = Partner(
        id="test-id",
        public_id="PART-001",
        legal_name="ООО Тест",
        inn="1234567890",
        verification_status="pending",
        rating=4.5,
        is_active=True
    )
    partner.created_at = datetime(2024, 1, 1, 12, 0, 0)
    
    result = partner.to_dict()
    
    assert result["public_id"] == "PART-001"
    assert result["legal_name"] == "ООО Тест"
    assert result["verification_status"] == "pending"
    assert result["rating"] == 4.5
    assert result["is_active"] is True
    assert "2024-01-01T12:00:00" in result["created_at"]
