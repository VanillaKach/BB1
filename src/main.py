from src.scraper import PerfumeScraper  # Было GoldAppleScraper
from src.saver import DataSaver


def main():
    print("Запуск процесса сбора данных...")

    # Используем новый класс
    scraper = PerfumeScraper(headless=False)

    # Сбор данных
    products = scraper.scrape(max_items=10)

    if not products:
        print("Товары не найдены или произошла ошибка.")
        return

    # Сохранение данных
    saver = DataSaver(output_dir="data")
    # Можно переименовать файл вывода
    saver.save_to_csv(products, filename="randewoo_parfume.csv")

    print("Процесс завершен.")


if __name__ == "__main__":
    main()
