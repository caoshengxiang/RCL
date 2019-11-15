#! /bin/bash
export PATH=$PATH:/usr/local/bin
cd /usr/local/workspace/rcl
nohup scrapy crawl rclgroup>> rclgroup.log 2>&1 &
