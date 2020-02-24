import re
import gzip
import json
import pickle
import tqdm
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.util import ngrams
# nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()


def preprocessing(stemmer, content, stop_words):
    cleaned_list = []
    pattern = '[^a-zA-Z0-9\-\ ]'
    content_str = re.sub(pattern, ' ', content).lower()
    tokens_list = nltk.word_tokenize(content_str)
    for token in tokens_list:
        if token not in stop_words:
            token = stemmer.stem(token)
            cleaned_list.append(token)
    return cleaned_list


unigram_dict = {}
bigram_dict = {}
trigram_dict = {}

gz_file = 'arxiv-metadata-oai-2020-02-11.json.gz'
with gzip.open(gz_file, 'rt', encoding='utf-8') as fin:
    for line in tqdm.tqdm(fin.readlines()):
        article = json.loads(line)
        doc_id = article['id']
        title = article['title']
        categories = article['categories']
        abstract = article['abstract']
        authors = article['authors']
        content = authors+title+abstract
        cleaned_words = preprocessing(ps, content, stop_words)
        str_content = " ".join(cleaned_words)

        for word in cleaned_words:
            if word not in unigram_dict:
                unigram_dict[word] = [{}, "", 1]
            else:
                unigram_dict[word][2] += 1

        bgs = nltk.bigrams(str_content.split())
        fdist = nltk.FreqDist(bgs)
        for k, v in fdist.items():
            if " ".join(k) not in bigram_dict:
                bigram_dict[" ".join(k)] = [{}, "", v]
            else:
                bigram_dict[" ".join(k)][2] += v

        tgs = ngrams(str_content.split(), 3)
        fdist = nltk.FreqDist(tgs)
        for k, v in fdist.items():
            if " ".join(k) not in trigram_dict:
                trigram_dict[" ".join(k)] = [{}, "", v]
            else:
                trigram_dict[" ".join(k)][2] += v
