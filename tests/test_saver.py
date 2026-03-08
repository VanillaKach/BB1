import pytest
import os
import csv
import tempfile
from typing import List  # Добавлен импорт List
from src.saver import DataSaver
from src.models import Product  # Добавлен импорт Product


class TestDataSaver:
    """Тесты для класса DataSaver."""

    @pytest.fixture
    def temp_dir(self):
        """Создает временную директорию для тестов."""
        dirpath = tempfile.mkdtemp()
        yield dirpath
        # Очистка не обязательна, так как /tmp чистится при перезагрузке,
        # но можно добавить shutil.rmtree(dirpath) если нужно.

    def save_to_csv(self, products: List[Product], filename: str = "products.csv") -> str:
        """
        Сохраняет список продуктов в CSV файл.
        Файл создается всегда (минимум с заголовком).
        :return: Полный путь к сохраненному файлу.
        """
        filepath = os.path.join(self.output_dir, filename)

        # Гарантируем создание директории, если её нет
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        fieldnames = [
            'url', 'name', 'price', 'rating',
            'description', 'instruction', 'country'
        ]

        try:
            # Открываем файл ВСЕГДА
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Пишем заголовок сразу

                if not products:
                    print("Нет данных для сохранения (файл создан с заголовком).")
                    return filepath

                for product in products:
                    writer.writerow(product.to_dict())

            print(f"Данные успешно сохранены в файл: {filepath}")
            return filepath
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            raise

    def test_save_empty_list(self, temp_dir, capsys):
        """Проверка сохранения пустого списка."""
        saver = DataSaver(output_dir=temp_dir)
        filepath = saver.save_to_csv([], filename="empty.csv")

        captured = capsys.readouterr()

        # 1. Проверяем, что выведено сообщение об отсутствии данных
        assert "Нет данных для сохранения" in captured.out

        # 2. Проверяем, что файл НЕ был создан (так как данных нет)
        # Это соответствует текущей логике кода в src/saver.py
        assert not os.path.exists(filepath)

    def test_save_creates_directory(self, tmp_path):
        """Проверка, что saver создает директорию, если её нет."""
        # Создаем путь к несуществующей подпапке
        new_dir = tmp_path / "new_subdir"
        filepath = new_dir / "test.csv"

        products = [
            Product(url="http://test.com", name="Test", price="100 ₽")
        ]

        saver = DataSaver(output_dir=str(new_dir))
        result_path = saver.save_to_csv(products, filename="test.csv")

        # Проверяем, что директория создалась
        assert os.path.exists(new_dir)
        assert os.path.exists(result_path)

        # Проверяем содержимое
        with open(result_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            assert "Test" in content
