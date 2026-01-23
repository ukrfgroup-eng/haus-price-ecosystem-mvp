# В начало файла добавьте:
import pytest

@pytest.mark.block_d  # Это тесты блока D
class TestInvoiceGenerator:
    # ... существующий код ...

@pytest.mark.block_d
class TestRevenueAnalytics:
    # ... существующий код ...

@pytest.mark.block_a  # Это тесты блока A
class TestFNSVerificationService:
    # ... существующий код ...


