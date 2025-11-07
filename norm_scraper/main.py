import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from norm_scraper.pipelines import PostgresPipeline
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    load_dotenv()
    # Указываем путь до проекта Scrapy
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'norm_scraper.settings'
    process = CrawlerProcess(get_project_settings())
    # Запускаем конкретный spider
    process.crawl('norm_spider')
    # Начинаем выполнение
    process.start()
    # Обновляем статусы после обновления
    current_base = PostgresPipeline()
    current_base.change_statuses()
    # Формируем файл с изменениями и отправляем заданным адресатам
    data_frame = current_base.fetch_data_from_db()
    excel_file = current_base.create_excel_file(data_frame)
    current_base.send_message(excel_file)
