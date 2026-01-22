import pytest

def test_simple():
    """Простейший тест"""
    assert 1 + 1 == 2

def test_imports():
    """Тест импортов"""
    try:
        # Попробуем импортировать наши модули
        from backend.services.invoice_generator import InvoiceGenerator
        print("✅ InvoiceGenerator импортирован успешно")
        assert True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        pytest.fail(f"Не удалось импортировать модули: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
