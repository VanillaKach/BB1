import csv
import os
from typing import List
from src.models import Product


class DataSaver:
    """Класс для сохранения списка товаров в CSV файл."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_csv(
        self, products: List[Product], filename: str = "products.csv"
    ) -> str:
        """
        Сохраняет список продуктов в CSV файл.
        :return: Полный путь к сохраненному файлу.
        """
        filepath = os.path.join(self.output_dir, filename)

        if not products:
            print("Нет данных для сохранения.")
            return filepath

        fieldnames = [
            "url",
            "name",
            "price",
            "rating",
            "description",
            "instruction",
            "country",
        ]

        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for product in products:
                    writer.writerow(product.to_dict())

            print(f"Данные успешно сохранены в файл: {filepath}")
            return filepath
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            raise
