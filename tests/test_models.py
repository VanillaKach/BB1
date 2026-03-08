import pytest
from src.models import Product


class TestProduct:
    """Тесты для модели Product."""

    def test_create_product(self):
        """Проверка создания объекта Product."""
        product = Product(
            url="https://example.com/product/1",
            name="Test Perfume",
            price="1000 ₽",
            rating="4.5",
            description="Test description",
            instruction="Use daily",
            country="France",
        )
        assert product.url == "https://example.com/product/1"
        assert product.name == "Test Perfume"
        assert product.price == "1000 ₽"
        assert product.rating == "4.5"

    def test_create_product_with_defaults(self):
        """Проверка создания объекта с пустыми полями."""
        product = Product(url="https://example.com/2", name="No Data", price="0 ₽")
        assert product.rating is None
        assert product.description is None
        assert product.country is None

    def test_clean_text(self):
        """Проверка очистки текста от лишних пробелов."""
        messy_text = "  Multiple   spaces\nand\tnewlines  "
        cleaned = Product.clean_text(messy_text)
        assert cleaned == "Multiple spaces and newlines"

    def test_clean_text_none(self):
        """Проверка обработки None."""
        assert Product.clean_text(None) is None
        assert Product.clean_text("") is None

    def test_to_dict(self):
        """Проверка конвертации в словарь."""
        product = Product(
            url="https://ex.com",
            name="Name",
            price="100 ₽",
            rating=None,
            description=None,
            instruction=None,
            country=None,
        )
        data = product.to_dict()
        assert data["url"] == "https://ex.com"
        assert data["name"] == "Name"
        assert data["rating"] == "Нет данных"  # Проверка замены None на строку
        assert data["description"] == "Нет данных"
