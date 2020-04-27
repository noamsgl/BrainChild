import io
import os
import string
import dateparser
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

    def articleTreeToString(pTagTrees):
        articleText = ""
        for tree in pTagTrees:
            trString = etree.tostring(tree, method="text", encoding='unicode', pretty_print=False, with_tail=False)
            verboseprint(trString)
            articleText += trString + " \n "
        return articleText

    if "latimes.com" in url:
        pTagTrees = tree.xpath("//div[@class='RichTextArticleBody-body RichTextBody']//p")
        articleText = articleTreeToString(pTagTrees)
        articleTitle = tree.xpath("//h1[@class='ArticlePage-headline']/text()")[0]
        articleAuthor = tree.xpath("//div[@class='ArticlePage-authorName']//a/span/text()")[0]
        articleDate = tree.xpath("//div[@class='ArticlePage-datePublished-day']/text()")[0]
        folderName = "LATIMES"

    elif "mondoweiss.net" in url:
        print(url)
        pTagTrees = tree.xpath("//div[contains(@class,'entry-content')]//p")
        articleText = articleTreeToString(pTagTrees)
        articleTitle = tree.xpath("//h1[contains(@class,'post-title')]/text()")[0]
        articleAuthor = tree.xpath("//a[@class='author url fn']/text()")[0]
        articleDate = tree.xpath("//a[@class='date-link']//time[@class='post-date']/text()")[0]
        folderName = "MONDOWEISS"

    elif "timesofisrael.com" in url:
        folderName = "TimesOfIsrael"
        pTagTrees = tree.xpath("/html/body//div[@class='the-content']//p[not(@class)]")
        articleText = articleTreeToString(pTagTrees)
        articleTitle = tree.xpath("//h1[@class='headline']/text()")[0]
        articleAuthor = tree.xpath("//span[@class='byline']/a/text()")[0]
        articleDate = tree.xpath("//span[@class='date']/text()")[0]
        folderName = "TOI"
    else:
        exit("unknown url type")

    p = dateparser.parse(articleDate)
    articleJson = {"text": articleText,
                   "title": articleTitle,
                   "url": url,
                   "author": articleAuthor,
                   "datetime": str(p),
                   "folder": folderName,
                   "filename": folderName + "_" + articleAuthor[:8] + "_" + [x for x in url.split('/') if x != ""][-1][:8] + "_" + str(p.date())}

    return articleJson


def scrapeAuthor(url, N=None):
    r = requests.get(url, timeout=2)
    tree = html.document_fromstring(r.text)

    if "mondoweiss.net" in url:
        articleTrees = tree.xpath("//h2[@class='post-title']//a")
        allLinks = [tr.get("href") for tr in articleTrees]
        verboseprint(allLinks)
        for link in allLinks[:N]:
            print(link)
            saveArticle(link)


def scrapeTopic(url):
    if "timesofisrael.com" in url:
        r = requests.get(url, timeout=2)
        try:
            page_html = r.text
            tree = html.document_fromstring(r.text)
            trXpath = tree.xpath("//div[@class='item template1 news']//div[@class='headline']//a")

            with open("scrapedTopic" + ".jsonl", "w", encoding="utf-8") as fp:
                writer = jsonlines.Writer(fp)
                for tr in trXpath[:]:
                    linkURL = tr.get("href")
                    json = scrapeArticle(linkURL)
                    if (json is not None):
                        writer.write(json)

        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
            print(r.status_code)


def saveArticle(url, savtetotxt=True, savetojson=True):
    formatDict = {"json": "JSONFormat",
                  "txt": "TXTFormat"}
    articleJson = scrapeArticle(url)

    if savtetotxt:
        folderDir = "/".join(["ScrapedData", formatDict["txt"], articleJson["folder"]])
        if not os.path.exists(folderDir):
            os.makedirs(folderDir)
        fileDir = "/".join([folderDir, articleJson["filename"]]) + ".txt"
        with open(fileDir, "w", encoding='utf-8') as fp:
            fp.write("{}\n{}\n{}\n{}\n{}".format(articleJson['title'], articleJson['author'], articleJson["datetime"],
                                                 articleJson['url'], articleJson['text']))
    if savetojson:
        folderDir = "/".join(["ScrapedData", formatDict["json"], articleJson["folder"]])
        if not os.path.exists(folderDir):
            os.makedirs(folderDir)
        fileDir = "/".join([folderDir, articleJson["filename"]]) + ".json"
        with open(fileDir, "w", encoding='utf-8') as fp:
            json.dump(articleJson, fp, ensure_ascii=False)


if __name__ == '__main__':
    verbose = True
    verboseprint = print if verbose else lambda *a, **k: None
    urls = [
        "https://www.timesofisrael.com/abbas-in-phone-call-blitz-to-prevent-israeli-annexation-in-west-bank/",
        "https://www.timesofisrael.com/unity-government-nears-completion-as-yamina-readies-to-bolt/",
        "https://www.timesofisrael.com/topic/trump-peace-plan/",
        "https://mondoweiss.net/2020/02/understanding-the-trump-deal-of-the-century-what-it-does-and-doesnt-say/",
        "https://www.latimes.com/opinion/story/2020-01-28/trumps-long-awaited-middle-east-peace-plan-dead-in-the-water",
        "https://mondoweiss.net/author/yaser-alashqar",
        "https://mondoweiss.net/author/yumnapatel",
        "https://mondoweiss.net/author/jonathan-cook/",
    ]
    for url in urls[:-1]:
        if "/author/" in url:
            scrapeAuthor(url)
        elif "/topic/" in url:
            scrapeTopic(url)
        else:
            saveArticle(url)