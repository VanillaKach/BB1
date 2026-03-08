import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """
    Модель данных для представления товара.
    Использует dataclass для автоматической генерации методов __init__, __repr__ и т.д.
    """
    url: str
    name: str
    price: str
    rating: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    country: Optional[str] = None

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для записи в CSV."""
        return {
            'url': self.url,
            'name': self.name,
            'price': self.price,
            'rating': self.rating or 'Нет данных',
            'description': self.description or 'Нет данных',
            'instruction': self.instruction or 'Нет данных',
            'country': self.country or 'Нет данных'
        }

    @classmethod
    def clean_text(cls, text: Optional[str]) -> Optional[str]:
        """
        Утилита для очистки текста от лишних пробелов и переносов строк.
        Использует регулярные выражения для нормализации whitespace.
        """
        if not text:
            return None
        # Заменяем множественные пробелы и переносы на один пробел
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned if cleaned else None
