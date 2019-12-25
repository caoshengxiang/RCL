# -*- coding: utf-8 -*-

BOT_NAME = 'RCL'
SPIDER_MODULES = ['RCL.spiders']
NEWSPIDER_MODULE = 'RCL.spiders'
# mongo 配置
MONGO_URI = '49.235.131.71:27017'
MONGO_DB = 'rcltest'
# 日志
import datetime
today = datetime.datetime.now()
log_file_path = '/opt/logs/scrapy_{}_{}_{}.log'.format(today.year, today.month, today.day)
LOG_LEVEL = 'WARNING'  # WARNING DEBUG
LOG_FILE = log_file_path
LOG_ENCODING = 'utf-8'
# 不能设置为true 否则会导致在scrapyd服务下无法运行
LOG_STDOUT = False
# USER_AGENT = 'RCL (+http://www.yourdomain.com)'
ROBOTSTXT_OBEY = False
# scrapy最大并发量
CONCURRENT_REQUESTS = 100
# Configure a delay for requests for the same website (default: 0)
# 下载延迟
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 0.15
# 默认： 8 将对任何单个域执行的并发（即，并发）请求的最大数量。
CONCURRENT_REQUESTS_PER_DOMAIN = 32
# 默认： 0,将对任何单个IP执行的并发（即，并发）请求的最大数量
# CONCURRENT_REQUESTS_PER_IP = 1
# 是否开启retry
RETRY_ENABLED = True
# 减少重试次数
RETRY_TIMES = 1
RETRY_HTTP_CODECS = [500, 502, 503, 504, 408, 401, 400, 403, 505,
                     302]  # 遇到什么http code时需要重试，默认是500,502,503,504,408,网络连接超时等

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.62 Safari/537.36'
}
# chrome浏览器驱动位置
# EXECUTABLE_PATH='D:/work/chromedriver.exe'
EXECUTABLE_PATH='/usr/bin/chromedriver'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'RCL.middlewares.RclSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'RCL.middlewares.RclDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'RCL.pipelines.MongoPipeline': 300,
    'RCL.pipelines.MysqlPipeline': 301
}

# mysql
DB_TYPE = 'mysql',
# 线上
USER = 'a111222',
PASSWORD = '!@#123QWEqwe',
HOST = 'rm-bp19hl3624ib44ai5o.mysql.rds.aliyuncs.com',
# 测试的mysql
# USER = 'root',
# PASSWORD = '123456Lq!',
# HOST = '120.79.92.101',
PORT = 3306,
DB_NAME = 'sp_out',
# 代理
XDAILI_URL = 'http://dec.ip3366.net/api/?key=22249951182224995118&getnum=50&area=1&order=2&splits=%2C'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False
# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
