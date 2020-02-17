import gzip
import json
import pickle
import tqdm
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
postings_lists = {}

def preprocessing(content):
    cleaned_list = []
    for i in content:
        i = i.lower()
        if i.isalpha() and i not in stop_words:
            i = ps.stem(i)
            cleaned_list.append(i)
    return cleaned_list

def Doc(id, term_freq):
    return {id: term_freq}


gz_file = 'arxiv-metadata-oai-2020-02-11.json.gz'
with gzip.open(gz_file, 'rt', encoding='utf-8') as fin:
    for line in tqdm.tqdm(fin.readlines()):
        article = json.loads(line)
        doc_id = article['id']
        title = article['title']
        categories = article['categories']
        abstract = article['abstract']
        authors = article['authors']

        content = nltk.word_tokenize(title + abstract)
        cleaned_words = preprocessing(content)
        for word in list(set(cleaned_words)):
            d = Doc(doc_id, [pos for pos, x in enumerate(cleaned_words) if x == word])

            if word in postings_lists:
                postings_lists[word].append(d)
            else:
                postings_lists[word] = [d]

js = json.dumps(postings_lists)
file = open('indexdict.txt', 'w')
file.write(js)
file.close()