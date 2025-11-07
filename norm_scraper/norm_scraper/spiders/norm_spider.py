from urllib.parse import urljoin
import scrapy
from ..items import NormScraperItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from decimal import Decimal


class NormSpider(scrapy.Spider):
    name = "norm_spider"
    allowed_domains = ["www.cameranorm.ru"]
    start_urls = ["https://www.cameranorm.ru/catalog/"]

    def __init__(self):
        super().__init__()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response):
        """Пройдемся по основным категориям"""
        categories = set(response.css('ul.menu-wrapper a::attr(href)').getall())
        categories_links = [f'https://www.cameranorm.ru{link}?display=block' for link in categories]
        for category_url in categories_links:
            if '/catalog/' in category_url:
                print(category_url)
                yield scrapy.Request(category_url, callback=self.parse_category, dont_filter=True)

    def parse_category(self, response):
        products = response.css('a.thumb.shine::attr(href)')
        if products:
            for link in products.getall():
                yield response.follow(link, callback=self.parse_product)
            # Переход на следующую страницу, если она доступна
            next_page_link = response.css('.nums ul.flex-direction-nav li.flex-nav-next a::attr(href)').get()
            if next_page_link:
                next_page_url = urljoin(response.url, next_page_link)
                yield scrapy.Request(next_page_url, callback=self.parse_category, dont_filter=True)

    def parse_product(self, response):
        """Собираем необходимую информацию о товаре"""
        item = NormScraperItem()
        # Артикул
        article = response.css('.item_block .article .value::text').get()
        item['article'] = article.strip() if article else ''
        # Наименование
        title = response.css('#pagetitle::text').get()
        item['title'] = title.strip() if title else ''
        # Описание
        description = response.css('.detail_text ::text').getall()
        clean_description = ''.join(description).replace('\xa0', '').strip()
        item['description'] = clean_description if clean_description else ''
        # Цена розничная
        retail_price = response.css('.price_matrix_block .price_group:first-child .price_value::text').get()
        if not retail_price or retail_price.strip() == '':
            retail_price = '0'
        else:
            retail_price = retail_price.strip().replace(' ', '').replace(',', '.')
        item['current_retail'] = Decimal(retail_price)
        # Минимальная оптовая цена
        dealer_price = response.css('.price_matrix_block .price_group.min .price_value::text').get()
        if not dealer_price or dealer_price.strip() == '':
            dealer_price = '0'
        else:
            dealer_price = dealer_price.strip().replace(' ', '').replace(',', '.')
        item['current_dealer'] = Decimal(dealer_price)
        # Фото продукта: получаем уникальные абсолютные ссылки
        photos_links = set(response.css('.item_slider a.popup_link.fancy::attr(href)').getall())
        full_photo_urls = [f'https://www.cameranorm.ru{link}' for link in photos_links]
        item['photo'] = ' '.join(full_photo_urls)
        # Ссылка на страницу товара
        link = response.css('meta[property="og:url"]::attr(content)').get()
        item['link'] = link.strip() if link else ''
        # Бренд
        brand_name = response.css('.brand img::attr(title)').get()
        item['brand'] = brand_name.strip() if brand_name else 'NORM'
        # Используем Selenium для манипуляции формой и вычисления количества товара
        self.driver.get(response.url)
        try:
            # Найти поле количества товара и установить большое значение
            quantity_field = self.driver.find_element(By.NAME, "quantity")
            quantity_field.clear()
            quantity_field.send_keys("10000000")
            # Дождаться, когда сервер обновит данные
            wait = WebDriverWait(self.driver, 10)
            plus_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "plus")))
            # Берём максимальное доступное количество товара
            max_quantity = plus_button.get_attribute("data-max")
            if not max_quantity or max_quantity.strip() == '':
                max_quantity = '0'
            else:
                max_quantity = max_quantity.strip().replace(' ', '').replace(',', '.')
            item['availability'] = Decimal(max_quantity) if max_quantity.isdigit() else Decimal('0')
        except Exception as e:
            print(f"Произошла ошибка при получении данных о наличии товара: {str(e)}")
            item['availability'] = Decimal('0')
        return item
