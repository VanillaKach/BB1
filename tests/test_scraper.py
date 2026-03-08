import os
import pytest
from unittest.mock import patch, MagicMock
from src.scraper import PerfumeScraper
from src.models import Product


class TestPerfumeScraper:
    """Тесты для скрапера PerfumeScraper."""

    @pytest.fixture
    def scraper(self):
        """Фикстура для создания экземпляра скрапера без запуска браузера."""
        # Мы патчим __init__ чтобы не запускать driver при создании объекта для тестов
        with patch.object(PerfumeScraper, "_init_driver", return_value=MagicMock()):
            s = PerfumeScraper()
            s.driver = MagicMock()  # Мок драйвера
            return s

    def test_extract_product_links(self, scraper):
        """Проверка извлечения ссылок из HTML."""
        html = """
        <html>
        <a href="/product/perfume-1">Link 1</a>
        <a href="/product/perfume-2">Link 2</a>
        <a href="/category/other">Other</a>
        </html>
        """
        links = scraper._extract_product_links(html)
        assert len(links) == 2
        assert "https://randewoo.ru/product/perfume-1" in links
        assert "https://randewoo.ru/product/perfume-2" in links
        assert "https://randewoo.ru/category/other" not in links

    def test_parse_product_page_full(self, scraper):
        """Проверка парсинга полной страницы товара."""
        html = """
        <html>
        <h1>Brand Name</h1>
        <div class="price">5000 ₽</div>
        <div class="description">Описание: Это лучший аромат.</div>
        <div class="instruction">Применение: Наносить на шею.</div>
        <div class="country">Страна: Франция</div>
        <script type="application/ld+json">{"ratingValue": "4.8"}</script>
        </html>
        """
        product = scraper._parse_product_page(html, "https://randewoo.ru/product/test")

        assert product is not None
        assert "Brand" in product.name
        assert "5000 ₽" in product.price
        assert "4.8" == product.rating
        assert "Франция" in product.country

    def test_parse_product_page_missing_data(self, scraper):
        """Проверка парсинга страницы с отсутствующими данными."""
        html = "<html><h1>Only Name</h1></html>"
        product = scraper._parse_product_page(html, "https://randewoo.ru/product/test")

        assert product.name is not None
        assert product.price == "0 ₽"
        assert product.rating is None
        assert product.country is None

    def test_fetch_html_mock(self, scraper):
        """Проверка метода _fetch_html с моком."""
        scraper.driver.page_source = "<html>Mocked Content</html>"
        result = scraper._fetch_html("https://example.com")
        assert "Mocked Content" in result
        scraper.driver.get.assert_called_once_with("https://example.com")

    def test_scrape_no_links(self, scraper, tmp_path, capsys):
        """Проверка поведения, если ссылки не найдены."""
        # Патчим output_dir для saver или просто проверяем логи скрапера
        # Здесь тестируем только логику скрапера
        scraper._fetch_html = lambda url: "<html><body>No products here</body></html>"

        # Временная папка для debug файла, чтобы не мусорить
        import tempfile
        old_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            products = scraper.scrape(max_items=5)
            assert products == []
            captured = capsys.readouterr()
            assert "Найдено ссылок: 0" in captured.out
            # Проверка создания файла
            assert os.path.exists("debug_randewoo.html")
        finally:
            os.chdir(old_cwd)

    def test_scrape_successful_flow(self, scraper):
        """Проверка успешного потока сбора данных."""
        # Делаем HTML максимально похожим на реальный, чтобы регексп сработал
        category_html = '''
        <html>
        <body>
        <div class="catalog">
            <a class="card" href="/product/test-1">Link 1</a>
            <a class="card" href="/product/test-2">Link 2</a>
        </div>
        </body>
        </html>
        '''
        product_html = '''
        <html>
        <body>
        <h1>Test Product Name</h1>
        <div class="price">1000 ₽</div>
        <script type="application/ld+json">{"ratingValue": "4.5"}</script>
        </body>
        </html>
        '''

        call_count = 0

        def mock_fetch(url):
            nonlocal call_count
            call_count += 1
            # Первый вызов - категория, остальные - товары
            return category_html if call_count == 1 else product_html

        scraper._fetch_html = mock_fetch

        products = scraper.scrape(max_items=1)

        # Мы ожидаем 1 товар, так как max_items=1
        assert len(products) == 1
        assert "Test" in products[0].name
        assert "1000 ₽" in products[0].price

    def test_fetch_html_network_error(self, scraper, capsys):
        """Проверка обработки сетевой ошибки."""

        def mock_get_error(url):
            raise Exception("Network Error")

        scraper.driver.get = mock_get_error

        result = scraper._fetch_html("http://error.com")
        assert result is None
        captured = capsys.readouterr()
        assert "Ошибка загрузки" in captured.out

    def test_fetch_html_timeout(self, scraper, capsys):
        """Проверка обработки таймаута ожидания элементов."""
        from selenium.common.exceptions import TimeoutException

        def mock_wait_timeout(*args, **kwargs):
            raise TimeoutException("Time out!")

        # Мокаем WebDriverWait
        with patch('src.scraper.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.side_effect = mock_wait_timeout

            # driver.get должен работать, чтобы вернуть page_source
            scraper.driver.page_source = "<html>Some content</html>"

            result = scraper._fetch_html("http://timeout.com")

            # Должен вернуть контент, даже если таймаут
            assert result is not None
            captured = capsys.readouterr()
            assert "Таймаут" in captured.out

    def test_init_driver_failure(self):
        """Проверка обработки ошибки при инициализации драйвера."""
        # Патчим webdriver.Firefox так, чтобы он выбрасывал исключение
        with patch('src.scraper.webdriver.Firefox') as mock_firefox:
            mock_firefox.side_effect = Exception("Browser failed to start")

            # Ожидаем, что при создании объекта вылетит исключение
            with pytest.raises(Exception, match="Browser failed to start"):
                # Мы не можем создать объект полностью, так как __init__ упадет
                # Поэтому тестируем только вызов метода внутри, если бы он был отдельно
                # Но так как это в __init__, просто проверяем, что исключение пробрасывается
                try:
                    with patch.object(PerfumeScraper, '_find_firefox_binary', return_value="/fake/path"):
                        with patch('src.scraper.Service'):
                            PerfumeScraper(headless=True)
                except Exception as e:
                    raise e
