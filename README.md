# BB1: Парсер парфюмерии (Randewoo)

Проект веб-скрапинга товаров из раздела "Парфюмерия" интернет-магазина Randewoo.ru.
Разработан для анализа ценности товаров, сбора данных о ценах, рейтингах и описаниях.

## 📋 Функционал
- Сбор данных о товарах (название, цена, рейтинг, описание, инструкция, страна).
- Использование регулярных выражений (Regex) для парсинга HTML.
- Сохранение результатов в формат CSV.
- Объектно-ориентированная архитектура (OOP).
- Покрытие тестами > 75%.

## 🛠 Технологии
- **Язык**: Python 3.11+
- **Библиотеки**: `selenium`, `webdriver-manager`, `pytest`, `pytest-cov`, `black`, `flake8`.
- **Браузер**: Firefox (через GeckoDriver).

## 📂 Структура проекта
```text
BB1/
├── src/
│   ├── __init__.py
│   ├── main.py          # Точка входа
│   ├── models.py        # Модель данных Product
│   ├── scraper.py       # Логика скрапинга и парсинга
│   └── saver.py         # Сохранение в CSV
├── tests/
│   ├── test_models.py
│   ├── test_scraper.py
│   └── test_saver.py
├── data/
│   └── randewoo_parfume.csv  # Итоговый файл с данными
├── .flake8              # Конфигурация линтера
├── pytest.ini           # Настройки тестов
├── requirements.txt     # Зависимости
└── README.md


## 🚀 Установка и запуск
1. Подготовка окружения
# Клонируйте репозиторий
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd BB1

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

## Запуск скрапера
python -m src.main

## Запуск тестов
# Прогон тестов с отчетом о покрытии
pytest --cov=src --cov-report=term-missing

# Проверка стиля кода
flake8 src tests
black src tests --check

📝 Примечание
Проект использует Selenium для обхода динамической загрузки контента. Для корректной работы требуется установленный браузер Firefox.
