import json
import os
import nltk
from tqdm import tqdm
import gensim


"""From Topic Modeling on Research Papers by Dipanjan Sarkar"""
# https://colab.research.google.com/github/dipanjanS/nlp_workshop_odsc19/blob/master/Module05%20-%20NLP%20Applications/Project04%20-%20Topic%20Modeling.ipynb#scrollTo=yooz_EzuQE8f
def normalize_corpus(papers):
    norm_papers = []
    for paper in tqdm(papers):
        paper = paper.lower()
        paper_tokens = [token.strip() for token in wtk.tokenize(paper)]
        paper_tokens = [wnl.lemmatize(token) for token in paper_tokens if not token.isnumeric()]
        paper_tokens = [token for token in paper_tokens if len(token) > 1]
        paper_tokens = [token for token in paper_tokens if token not in stop_words]
        paper_tokens = list(filter(None, paper_tokens))
        if paper_tokens:
            norm_papers.append(paper_tokens)

    return norm_papers



def loadArticles(format="json"):
    articles = []
    if format == "txt":
        base = "ScrapedData/TXTFormat/"
        folders = os.listdir(base)
        for folder in folders:
            file_names = os.listdir(base + folder)
            for file_name in file_names:
                with open(base + folder + "/" + file_name, encoding='utf-8', mode='r+') as fp:
                    data = fp.read()
                    articles.append(data)
    elif format == "json":
        base = "ScrapedData/JSONFormat/"
        folders = os.listdir(base)
        for folder in folders:
            file_names = os.listdir(base + folder)
            for file_name in file_names:
                with open(base + folder + "/" + file_name, encoding='utf-8', mode='r+') as fp:
                    articleJson = json.load(fp)
                    articles.append(articleJson["text"])
    return articles




if __name__ == '__main__':
    articles = loadArticles()
    stop_words = nltk.corpus.stopwords.words('english')
    wtk = nltk.tokenize.RegexpTokenizer(r'\w+')
    wnl = nltk.stem.wordnet.WordNetLemmatizer()

    norm_articles = normalize_corpus(articles)
    print(len(norm_articles))
    print(norm_articles[0][:50])

    bigram = gensim.models.Phrases(norm_articles, min_count=20, threshold=20, delimiter=b'_')
    bigram_model = gensim.models.phrases.Phraser(bigram)

    print(bigram_model[norm_articles[0][:50]])
