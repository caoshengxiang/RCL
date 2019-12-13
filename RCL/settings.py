# -*- coding: utf-8 -*-
import datetime

# Scrapy settings for RCL project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'RCL'

SPIDER_MODULES = ['RCL.spiders']
NEWSPIDER_MODULE = 'RCL.spiders'

# mongo 配置
MONGO_URI = '49.235.131.71:27017'
MONGO_DB = 'rcltest'

# 日志
today = datetime.datetime.now()
log_file_path = '/opt/logs/scrapy_{}_{}_{}.log'.format(today.year, today.month, today.day)
LOG_LEVEL = 'DEBUG' #WARNING DEBUG
LOG_FILE = log_file_path
LOG_ENCODING = 'utf-8'
LOG_STDOUT = True
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'RCL (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 0.2

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16  # 默认： 8 将对任何单个域执行的并发（即，并发）请求的最大数量。
# CONCURRENT_REQUESTS_PER_IP = 1  # 默认： 0,将对任何单个IP执行的并发（即，并发）请求的最大数量

RETRY_ENABLED = True  # 是否开启retry
RETRY_TIMES = 2  # 重试次数
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

# mysql
DB_TYPE = 'mysql',
USER = 'a111222',
PASSWORD = '!@#123QWEqwe',
HOST = 'rm-bp19hl3624ib44ai5o.mysql.rds.aliyuncs.com',
# USER = 'root',
# PASSWORD = '1223456Lq!',
# HOST = '120.79.92.101',
PORT = 3306,
DB_NAME = 'sp_out',

# 代理
XDAILI_URL = 'http://dec.ip3366.net/api/?key=22249951182224995118&getnum=50&area=1&order=2&splits=%2C'
