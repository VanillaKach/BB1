import pytest
from unittest.mock import patch, MagicMock
from src.main import main


@patch("src.main.PerfumeScraper")
@patch("src.main.DataSaver")
def test_main_success(mock_saver_class, mock_scraper_class, capsys):
    """Тест успешного выполнения main."""
    # Настройка моков
    mock_product = MagicMock()
    mock_product.url = "http://test.com"
    mock_scraper = MagicMock()
    mock_scraper.scrape.return_value = [mock_product]
    mock_scraper_class.return_value = mock_scraper

    mock_saver = MagicMock()
    mock_saver_class.return_value = mock_saver

    main()

    captured = capsys.readouterr()
    assert "Запуск процесса сбора данных" in captured.out
    assert "Процесс завершен" in captured.out
    mock_scraper.scrape.assert_called_once()
    mock_saver.save_to_csv.assert_called_once()


@patch("src.main.PerfumeScraper")
def test_main_no_products(mock_scraper_class, capsys):
    """Тест, когда товары не найдены."""
    mock_scraper = MagicMock()
    mock_scraper.scrape.return_value = []
    mock_scraper_class.return_value = mock_scraper

    main()

    captured = capsys.readouterr()
    assert "Товары не найдены" in captured.out
