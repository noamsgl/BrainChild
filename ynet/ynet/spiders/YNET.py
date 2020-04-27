# -*- coding: utf-8 -*-
import scrapy


class YnetSpider(scrapy.Spider):
    name = 'YNET'
    allowed_domains = ['https://www.ynetnews.com/article/BkpdBkId8']
    start_urls = ['https://www.ynetnews.com/article/BkpdBkId8/']

    def parse(self, response):
        print("\n")
        print("HTTP STATUS: " + str(response.status))
        print(response.css("title::text").get())
        print(response.xpath("//div[contains(@class,'authors')]/text()").get())
        print("\n")
