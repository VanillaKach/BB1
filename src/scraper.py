import re
import time
import random
import os
import shutil
import tempfile
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager

from src.models import Product


class PerfumeScraper:
    """
    Скрапер для сбора данных о парфюмерии с Randewoo.ru
    """

    # ИСПРАВЛЕННЫЙ URL (как на твоем скриншоте)
    BASE_URL = "https://randewoo.ru"
    CATEGORY_URL = "https://randewoo.ru/category/parfyumeriya"

    def __init__(self, headless: bool = False):
        self.products: List[Product] = []
        self.driver = None
        try:
            self.driver = self._init_driver(headless)
        except Exception as e:
            print(f"❌ Критическая ошибка инициализации драйвера: {e}")
            raise

    def _find_firefox_binary(self) -> str:
        possible_paths = [
            "/usr/bin/firefox",
            "/snap/bin/firefox",
            shutil.which("firefox")
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        raise FileNotFoundError("Firefox не найден!")

    def _init_driver(self, headless: bool) -> webdriver.Firefox:
        options = Options()
        if headless:
            options.add_argument("--headless")

        # Временный профиль
        temp_profile_dir = tempfile.mkdtemp(prefix="selenium_ff_profile_")
        options.add_argument("-profile")
        options.add_argument(temp_profile_dir)

        # Настройки
        options.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0")
        options.set_preference("javascript.enabled", True)
        # Отключаем уведомления, чтобы не мешали
        options.set_preference("dom.webnotifications.enabled", False)

        firefox_binary = self._find_firefox_binary()
        options.binary_location = firefox_binary

        print(f"🦊 Браузер: {firefox_binary}")
        print(f"📂 Профиль: {temp_profile_dir}")

        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(1920, 1080)
        print("✅ Браузер запущен!")
        return driver

    def _fetch_html(self, url: str) -> Optional[str]:
        if not self.driver:
            return None

        try:
            print(f"   🔄 Загрузка: {url}")
            self.driver.get(url)

            # Ждем появления товаров.
            # На Randewoo карточки обычно имеют класс .product-item или ссылку /product/
            # Попробуем универсальный селектор: ссылка, содержащая '/product/'
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/product/']"))
                )
                print("   ✅ Товары найдены на странице.")
            except TimeoutException:
                print("   ⚠️ Таймаут: элементы товаров не появились за 20 сек.")
                # Не прерываем выполнение, пробуем парсить то, что есть

            # Даем время на полную отрисовку и подгрузку картинок/цен
            time.sleep(random.uniform(3.0, 5.0))

            return self.driver.page_source

        except WebDriverException as e:
            print(f"   ❌ Ошибка сессии WebDriver: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Ошибка загрузки: {e}")
            return None

    def _extract_product_links(self, html: str) -> List[str]:
        if not html or len(html) < 100:
            return []

        links = []
        # Ищем ссылки вида /product/...
        pattern = r'href="(/product/[^"]+)"'
        matches = re.findall(pattern, html, re.IGNORECASE)

        for match in matches:
            full_url = f"{self.BASE_URL}{match}"
            if full_url not in links:
                links.append(full_url)

        return links

    def _parse_product_page(self, html: str, url: str) -> Optional[Product]:
        if not html:
            return None

        # 1. Название (h1)
        name_pattern = r'<h1[^>]*>(.*?)</h1>'
        name_match = re.search(name_pattern, html, re.DOTALL | re.IGNORECASE)
        name = Product.clean_text(name_match.group(1)) if name_match else "Не указано"

        # 2. Цена (цифры + руб/₽)
        price_pattern = r'(\d[\d\s]*\.?\d*)\s*(?:руб|₽|RUB)'
        price_match = re.search(price_pattern, html, re.IGNORECASE)
        price = price_match.group(0) if price_match else "0 ₽"

        # 3. Рейтинг
        rating_match = re.search(r'"ratingValue"\s*:\s*"(\d\.?\d*)"', html)
        if not rating_match:
            rating_match = re.search(r'(\d\.?\d*)\s*(?:из|of)\s*\d', html, re.IGNORECASE)
        rating = rating_match.group(1) if rating_match else None

        # 4. Описание
        # Ищем блок после слова "Описание"
        desc_pattern = r'(?:Описание|Description)[^>]*?</div>\s*<div[^>]*>([\s\S]*?)</div>'
        desc_match = re.search(desc_pattern, html, re.IGNORECASE)
        description = Product.clean_text(desc_match.group(1)) if desc_match else None

        if not description:
            meta_desc = re.search(r'<meta name="description" content="([^"]+)"', html)
            if meta_desc:
                description = Product.clean_text(meta_desc.group(1))

        # 5. Инструкция (может отсутствовать)
        instr_pattern = r'(?:Инструкция|Способ применения|Применение)[^>]*?</div>\s*<div[^>]*>([\s\S]*?)</div>'
        instr_match = re.search(instr_pattern, html, re.IGNORECASE)
        instruction = Product.clean_text(instr_match.group(1)) if instr_match else None

        # 6. Страна
        country_pattern = r'(?:Страна|Производитель)[^:]*:\s*([^<]+)'
        country_match = re.search(country_pattern, html, re.IGNORECASE)
        country = Product.clean_text(country_match.group(1)) if country_match else None

        return Product(
            url=url,
            name=name,
            price=price,
            rating=rating,
            description=description,
            instruction=instruction,
            country=country
        )

    def scrape(self, max_items: int = 10) -> List[Product]:
        if not self.driver:
            print("❌ Драйвер не инициализирован.")
            return []

        print(f"🚀 Старт скрапинга: {self.CATEGORY_URL}")
        all_products = []

        html = self._fetch_html(self.CATEGORY_URL)

        if not html:
            print("❌ Не удалось получить HTML категории.")
            self.driver.quit()
            return []

        links = self._extract_product_links(html)
        print(f"🔗 Найдено ссылок: {len(links)}")

        if not links:
            filename = "debug_randewoo.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 HTML сохранен в {filename}")
            self.driver.quit()
            return []

        links_to_parse = links[:max_items]

        for i, link in enumerate(links_to_parse, 1):
            print(f"📦 Товар {i}/{len(links_to_parse)}")
            product_html = self._fetch_html(link)
            if product_html:
                product = self._parse_product_page(product_html, link)
                if product:
                    all_products.append(product)

        try:
            self.driver.quit()
            print("🛑 Браузер закрыт.")
        except:
            pass

        print(f"✅ Готово! Собрано товаров: {len(all_products)}")
        return all_products
