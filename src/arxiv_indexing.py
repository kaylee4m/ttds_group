import gzip
import json
import pickle
import tqdm
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from utils import *


class PostingElement:
    """
        Data structure for one element in posting list
    """

    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.is_author = False
        self.positions = []
        raise NotImplementedError

    def add():
        pass


class PostingList:
    """
        Data structure for posting list
    """

    def __init__(self, term):
        self.term = term
        raise NotImplementedError

    def add_doc(self, doc_id):
        raise NotImplementedError

    def encode(self):
        """
            Apply index compression.
            @return: byte array to save to disk
        """
        raise NotImplementedError
        return

    @staticmethod
    def decode(byte_seq):
        """
            Decode index compression.
            @return: PostingList object
        """
        raise NotImplementedError
        return PostingList()

    def __str__(self):
        return ""

    def save_index(self, index_dir):
        """
            Save a posting list into memory or one file
        """


def get_term_key(term):
    """
        convert a term into key. Used to 1. find posting list in cache 2.
    """
    return term


def get_term_index_file(key, index_dir):
    """
        Find the index file associated with this key,
    """
    pass


def get_posting_list(term):
    """
        Get a posting list using term as the key
    """
    global cached_posting_list
    key = get_term_key(term)
    if key in cached_posting_list:
        # TODO: load
        raise NotImplementedError
    else:
        # TODO load from disk using get_term_index_file, decode it with PostingList.decode()
        #  and add to cache
        # Remember to save to disk if some cached posting is discarded
        raise NotImplementedError


def preprocessing(stemmer, content, stop_words):
    cleaned_list = []
    for i in content:
        i = i.lower()
        if i.isalpha() and i not in stop_words:
            i = stemmer.stem(i)
            cleaned_list.append(i)
    return cleaned_list


def Doc(id, term_freq):
    return {id: term_freq}


def process_one_article(article):
    """
        Process one article
    """

    # TODO: edit these
    doc_id = article['id']
    title = article['title']
    categories = article['categories']
    abstract = article['abstract']
    authors = article['authors']

    content = nltk.word_tokenize(title + abstract)
    cleaned_words = preprocessing(content)
    for word in list(set(cleaned_words)):
        pl = get_posting_list(word)
        ...
        d = Doc(doc_id, [pos for pos, x in enumerate(
            cleaned_words) if x == word])

        if word in postings_lists:
            postings_lists[word].append(d)
        else:
            postings_lists[word] = [d]

    raise NotImplementedError


def build_index(gz_file, index_dir):
    """
        To build index using All data
    """
    raise NotImplementedError


def update_index(gz_file, index_dir):
    """
        To update current index using new data. 
        Expect: All doc id are new 
    """
    raise NotImplementedError


def build_index_main(args):
    global cached_posting_list
    cfg = get_config(args)
    nltk.download('stopwords')

    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    postings_lists = {}

    gz_file = cfg['ALL_DATA']
    index_dir = cfg['INDEX_DIR']
    with gzip.open(gz_file, 'rt', encoding='utf-8') as fin:
        for line in tqdm.tqdm(fin.readlines()):
            article = json.loads(line)
            process_one_article(article)

    js = json.dumps(postings_lists)
    file = open('indexdict.txt', 'w')
    file.write(js)
    file.close()


def update_index_main(args):
    pass


if __name__ == "__main__":
    global cached_posting_list
    cached_posting_list = {}
    args = args_build_index()
    build_index_main(args)
