import io
import string

import chardet
import nltk, re, pprint
import unicodedata
from lxml import etree, html
from lxml.html.soupparser import fromstring
from nltk import word_tokenize
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, UnicodeDammit
import json, jsonlines




def scrapeArticle(url):
    try:
        r = requests.get(url, timeout=2, headers={'User-Agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        exit("Connection refused")

    tree = html.document_fromstring(r.text)
    if "latimes.com" in url:
        trXpath = tree.xpath("//div[@class='RichTextArticleBody-body RichTextBody']//p")
        if (len(trXpath) == 0):
            return None
        print("length: ", len(trXpath))
        articleText = ""
        for tr in trXpath:
            toprint = etree.tostring(tr, method="text", encoding='unicode', pretty_print=False, with_tail=False)
            # print(type("\n"))
            print(toprint)
            articleText += toprint + " \n "
        articleTitle = tree.xpath("//h1[@class='ArticlePage-headline']/text()")[0]
        articleAuthor = tree.xpath("//div[@class='ArticlePage-authorName']//a/span/text()")[0]
        articleDate = tree.xpath("//div[@class='ArticlePage-datePublished-day']/text()")[0]
        print("scraped: {}, by {}, from {}".format(url, articleAuthor, articleDate))

    elif "mondoweiss.net" in url:
        page_html = r.text
        soup = BeautifulSoup(page_html, 'html.parser')
        divEntryContent = soup.select('div[class*="entry"]')[0]
        # entryContentParagraphs = soup.find_all("p", attrs={'class': None})
        entryContentDivs = divEntryContent.find_all("div")
        for div in entryContentDivs:
            div.decompose()
        articleText = divEntryContent.get_text()

    elif "timesofisrael.com" in url:
        trXpath = tree.xpath("/html/body//div[@class='the-content']//p[not(@class)]")
        if (len(trXpath) == 0):
            return None
        print("length: ", len(trXpath))
        articleText = ""
        for tr in trXpath:
            toprint = etree.tostring(tr, method="text", encoding=str, pretty_print=False, with_tail=False)
            articleText += toprint + " \n "
        articleTitle = tree.xpath("//h1[@class='headline']/text()")[0]
        articleAuthor = tree.xpath("//span[@class='byline']/a/text()")[0]
        articleDate = tree.xpath("//span[@class='date']/text()")[0]
        print("scraped: {}, by {}, from {}".format(url, articleAuthor, articleDate))
        json = {"text": articleText,
                "title": articleTitle,
                "url": url,
                "author": articleAuthor,
                "date": articleDate,
                "folder": "TimesOfIsrael",
                "filename": url.split('/')[-1][:12] }
        return json

    else:
        exit("unknown url type")

    articleJson = {"text": articleText,
                   "url": url,
                   "author": articleAuthor,
                   "date": articleDate}
    return articleJson


def scrapeAuthor(url, N=None):
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

            with open("scrapedTopic" + ".jsonl", "w", encoding="unicode") as fp:
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


def saveArticle(url, format="json"):
    articleJson = scrapeArticle(url)
    if format == 'json':
        with open("scrapedArticle.json", "w", encoding='utf-8') as fp:
            json.dump(scrapeArticle(url), fp, ensure_ascii=False)

    elif format == 'txt':
        with open("scrapedArticle.txt", "w", encoding='utf-8') as fp:
            fp.write("{}\n{}\n{}\n{}".format(articleJson['title'],articleJson['author'],articleJson['url'],articleJson['text']))

    else:
        exit("unknown format")


if __name__ == '__main__':
    # url2 = "https://mondoweiss.net/author/yumnapatel"
    # url2 = "https://mondoweiss.net/author/yaser-alashqar"
    # url = "https://www.timesofisrael.com/unity-government-nears-completion-as-yamina-readies-to-bolt/"
    url = "https://www.timesofisrael.com/abbas-in-phone-call-blitz-to-prevent-israeli-annexation-in-west-bank/"
    # url = "https://www.timesofisrael.com/topic/trump-peace-plan/"
    # url = "https://www.latimes.com/opinion/story/2020-01-28/trumps-long-awaited-middle-east-peace-plan-dead-in-the-water"
    text = saveArticle(url, "txt")
    # print(text)
    # url = "https://mondoweiss.net/2020/04/after-weeks-of-ignoring-its-palestinian-citizens-israel-to-step-up-testing-in-arab-towns"
    # downloadArticle(url)
