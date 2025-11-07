BOT_NAME = "norm_scraper"

SPIDER_MODULES = ["norm_scraper.spiders"]
NEWSPIDER_MODULE = "norm_scraper.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 2  # Задержка между запросами 2 секунды
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # Параллельных запросов одновременно не больше 2-х
AUTOTHROTTLE_ENABLED = True  # Автоматическое управление скоростью
AUTOTHROTTLE_START_DELAY = 5  # Начальная задержка в секундах
AUTOTHROTTLE_MAX_DELAY = 60  # Максимальная задержка в секундах

DOWNLOAD_TIMEOUT = 30  # увеличенная максимальная длительность одного запроса
DNSCACHE_ENABLED = True  # кэширование DNS ускорит последующие запросы
DNS_TIMEOUT = 60         # ограничение времени ожидания DNS-запросов
RETRY_TIMES = 3          # автоматические повторы неудачных запросов
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 10054]  # коды ошибок для автоматического повтора

# Запись данных в базу данных
ITEM_PIPELINES = {
   'norm_scraper.pipelines.PostgresPipeline': 300,
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
# Включение промежуточного ПО
DOWNLOADER_MIDDLEWARES = {
    # ... Other middlewares
    'norm_scraper.middlewares.UARotatorMiddleware': 400,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
