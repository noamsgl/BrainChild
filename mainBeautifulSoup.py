import io
import nltk, re, pprint
from lxml import etree, html
from lxml.html.soupparser import fromstring
from nltk import word_tokenize
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, UnicodeDammit
import json, jsonlines


def isEntryContent(classmethod):
    print(classmethod)
    return re.compile("entry").search(classmethod)


def downloadArticle(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    articleText = scrapeArticle(url)
    jsonToReturn = {"text": articleText}
    with open(url[-10:] + ".json", "w", encoding="utf-8") as write_file:
        json.dump(jsonToReturn, write_file)


def scrapeArticle(url):
    if "mondoweiss.net" in url:
        req = Request(url, headers={'User-Agent': 'Chrome/81.0.4044.92'})
        page_html = urlopen(req).read()
        soup = BeautifulSoup(page_html, 'html.parser')
        divEntryContent = soup.select('div[class*="entry"]')[0]
        # entryContentParagraphs = soup.find_all("p", attrs={'class': None})
        entryContentDivs = divEntryContent.find_all("div")
        for div in entryContentDivs:
            div.decompose()
        articleText = divEntryContent.get_text()

    if "timesofisrael.com" in url:
        r = requests.get(url, timeout=2)
        try:
            page_html = r.text
            converted = UnicodeDammit(page_html)
            tree = html.document_fromstring(r.text)
            # trXpath = tree.xpath("/html/body//div[@class='the-content']//text()")
            build_text_list = etree.XPath("//text()")
            # print(build_text_list(tree))
            trXpath = tree.xpath("/html/body//div[@class='the-content']//p[not(@class)]")
            if (len(trXpath) == 0):
                return None
            print("length: ", len(trXpath))
            articleText = ""
            for tr in trXpath:
                toprint = etree.tostring(tr, method="text", encoding='unicode', pretty_print=False, with_tail=False)
                articleText += toprint + " \n "
            articleAuthor = tree.xpath("//span[@class='byline']/a/text()")[0]
            articleDate = tree.xpath("//span[@class='date']/text()")[0]
            print("scraped: {}, by {}, from {}".format(url, articleAuthor, articleDate))
            json = {"text": articleText,
                    "url": url,
                    "author": articleAuthor,
                    "date": articleDate}
            return json

        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
            print(r.status_code)


def scrapeAuthor(url, N=None):
    N = 4
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')

    with open("scrapedAuthor" + ".jsonl", "w", encoding="utf-8") as fp:
        writer = jsonlines.Writer(fp)
        jsonToReturn = {}
        if "mondoweiss.net" in url:
            allLinks = soup.select('a[rel="bookmark"]')
            for link in allLinks[:N]:
                ### print link title currently being scraped
                print(link.prettify())
                articleText = scrapeArticle(link['href'][:-1])
                print(articleText)
                json = {"text": articleText}
                writer.write(json)
                # downloadArticle(link['href'][:-1])


def scrapeTopic(url):
    if "timesofisrael.com" in url:
        r = requests.get(url, timeout=2)
        try:
            page_html = r.text
            tree = html.document_fromstring(r.text)
            trXpath = tree.xpath("//div[@class='item template1 news']//div[@class='headline']//a")

            with open("scrapedTopic" + ".jsonl", "w", encoding="utf-8") as fp:
                writer = jsonlines.Writer(fp)
                jsonToReturn = {}
                for tr in trXpath[:]:
                    linkURL = tr.get("href")
                    json = scrapeArticle(linkURL)
                    if (json is not None):
                        writer.write(json)

        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
            print(r.status_code)


if __name__ == '__main__':
    # url2 = "https://mondoweiss.net/author/yumnapatel"
    # url2 = "https://mondoweiss.net/author/yaser-alashqar"
    url = "https://www.timesofisrael.com/unity-government-nears-completion-as-yamina-readies-to-bolt/"
    # url = "https://www.timesofisrael.com/abbas-in-phone-call-blitz-to-prevent-israeli-annexation-in-west-bank/"
    url = "https://www.timesofisrael.com/topic/trump-peace-plan/"

    text = scrapeTopic(url)
    # print(text)
    # url = "https://mondoweiss.net/2020/04/after-weeks-of-ignoring-its-palestinian-citizens-israel-to-step-up-testing-in-arab-towns"
    # downloadArticle(url)
