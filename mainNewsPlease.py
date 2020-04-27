import json
from newspaper import Article
from newsplease import NewsPlease
url = "https://www.nytimes.com/2020/04/21/nyregion/coronavirus-jews-hasidic-ny.html"

# article1 = Article(url)
# article1.download()

article2 = NewsPlease.from_url(url)
with open("output.txt", "w+", encoding="utf-8") as fp:
    fp.write(article2.maintext)
print(article2.maintext)
i = 5
# with open("dumphere.json","w+", encoding='utf-8') as fp:
#     json.dump(article, fp)