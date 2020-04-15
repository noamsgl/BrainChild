import scrapy
from lxml import html, etree
import requests

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/tag/humor/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'author': quote.xpath('span/small/text()').get(),
                'text': quote.css('span.text::text').get(),
            }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

if __name__ == '__main__':
    page_html = requests.get("https://raw.githubusercontent.com/PacktPublishing/Python-Web-Scraping-Cookbook/master/www/planets.html").text
    tree = html.fromstring(page_html)
    tableTree = tree.xpath("/html/body/div/table/tr[@class='planet']")
    stringofTree = etree.tostring(tableTree[0])
    x = 5