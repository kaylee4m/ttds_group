import gzip
import json
import pickle
import tqdm
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from utils import *
import hashlib
from cachetools import LFUCache


class PostingElement:
    """
        Data structure for one element in posting list
    """

<<<<<<< HEAD
    def __init__(self, doc_id, author=False):
=======
    def __init__(self, doc_id, cate, author=False):
>>>>>>> d5f6d495ef1925c44a1fd0ffb613ad139f0b3cc3
        self.doc_id = doc_id
        self.author = author
        self.positions = []

    def add_pos(self, pos):
        """Add one position to positions

        Arguments:
            pos {int} -- [description]
        """

        self.positions.append(pos)


class PostingList:
    """
        Data structure for posting list
    """

    def __init__(self, term):
        self.term = term
        # TODO: TO be decided whether we use a list or a binary tree
        self.doc_ids = {}  # doc_id: idx in list
        self.doc_list = []
        #raise NotImplementedError

    def get_doc_posting(self, article):
        """If a doc is recorded, return it; if not, create the postingElement for it and return it

        Arguments:
            article {dict} -- [description]

        Returns:
            [type] -- [description]
        """
        doc_id = article['id']
<<<<<<< HEAD
        if doc_id not in self.doc_ids:
            self.doc_list.append(PostingElement(doc_id))
=======
        cate = article['categories']
        if doc_id not in self.doc_ids:
            self.doc_list.append(PostingElement(doc_id, cate))
>>>>>>> d5f6d495ef1925c44a1fd0ffb613ad139f0b3cc3
            self.doc_ids[doc_id] = len(self.doc_list)-1
        return self.doc_list[self.doc_ids[doc_id]]

    def get_posting_by_docid(self, doc_id):
        if doc_id not in self.doc_ids:
            return None
        return self.doc_list[self.doc_ids[doc_id]]

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

    def get_doc_ids(self):
        """
            Return all doc ids in this pl
        """
        raise NotImplementedError
        return []

    def get_postings(self, year_range: str=""):
        """
            Return all postings
            if year range is specified as "2019-2020" only return those published in these years
        """
        raise NotImplementedError
        return []

    def __str__(self):
        return ""

def get_doc_word_count()


def get_term_key(term):
    """
        convert a term into key. Terms with the same key will be saved into the same file.
        Used to find posting list group in cached_posting_list.
        See Index Storage and Compression section in report.
    """
    obj = hashlib.md5()
    obj.update(term.encode("utf-8"))
    key = int(obj.hexdigest(), 16) % (10 ** 5)
    return key


def get_term_index_file(key, index_dir: str):
    """
        Find the index file associated with this key.
        A file contains many posting lists (each associated with one term)
    """
    # TODO load from disk
    #  decode  with PostingList.decode()
    # and return group of pls
    with open(index_dir+str(key), 'r') as dictfile:
        js = dictfile.read()
        pl_object = json.loads(js)#load posting list object using json
    pl_group = pl_object.decode()
    return pl_group


def get_posting_list(term: str, index_dir):
    """        Get a posting list using term as the key


    Arguments:
        term {[type]} -- [description]
        index_dir {[type]} -- [description]

    Raises:
        NotImplementedError: [description]

    Returns:
        posting_list: PostingList -- The posting_list for the term.
                         Return None if not presented in index 
    """
    global cached_posting_list
    key = get_term_key(term)
    if key in cached_posting_list:
        # DONE: load
        d = cached_posting_list[key]
        posting_list = d[term]
    else:
        pl_group = get_term_index_file(key, index_dir)
        # TODO add to cache
        cached_posting_list[key] = pl_group
        # Remember to save **asynchronously** to disk if some cached posting is discarded
        posting_list = pl_group[term]
    return posting_list


def save_posting_list_group(key,pl_group, index_dir):
    """Save a posting list group to disk

    Arguments:
        pl_group {dict} -- Dictionary of posting lists.

    Raises:
        NotImplementedError: [description]
    """
    saved_group = json.dumps(pl_group)
    file = open(index_dir+"/"+str(key), 'w')
    file.write(saved_group)
    file.close()




def preprocessing(stemmer, content, stop_words):
    cleaned_list = []
    for i in content:
        i = i.lower()
        if i.isalpha() and i not in stop_words:
            i = stemmer.stem(i)
            cleaned_list.append(i)
    return cleaned_list


class BuildIndex:
    def __init__(self, cfg):
        self.cfg = cfg

    def Doc(self, id, term_freq):
        return {id: term_freq}

    def process_one_article(self, article, stop_words, stemmer):
        """
            Process one article
        """
        doc_id = article['id']
        title = article['title']
        categories = article['categories']
        abstract = article['abstract']
        authors = article['authors']

        # TODO: combine title, author and content
        # use get_doc_year to get year from doc id,
        # before add year into index, make it special by using get_sp_term. "08" -> "#08"
        # use get_cat_tag to get special term for category
        content = nltk.word_tokenize(title + abstract)
        cleaned_words = preprocessing(content, stop_words, stemmer)
        for pos, word in enumerate(cleaned_words):
            pl: PostingList = get_posting_list(word, self.cfg['INDEX_DIR'])
            doc_posting: PostingElement = pl.get_doc_posting(article)
            doc_posting.add_pos(pos)
        # TODO: build index for category?

    def build_index(self):
        """
            To build index using All data
        """

        # TODO Only need to download once, please check this
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))
        ps = PorterStemmer()
        with gzip.open(gz_file, 'rt', encoding='utf-8') as fin:
            for line in tqdm.tqdm(fin.readlines()):
                article = json.loads(line)
                self.process_one_article(article, stop_words, ps)

    def update_index(self, gz_file, index_dir):
        """
            To update current index using new data. 
            Expect: All doc id are new 
        """
        raise NotImplementedError

    def build_index_main(self, args):
        # DONE
        global cached_posting_list
        self.build_index()
        # save all the rest in cache
        for k, pl in cached_posting_list.items():
            assert type(pl) == PostingList
            save_posting_list_group(k,pl, self.cfg['INDEX_DIR'])

    def update_index_main(self, args):
        pass


if __name__ == "__main__":
    global cached_posting_list
    args = args_build_index()
    cfg = get_config(args)
    # dict of group of posting lists
    cached_posting_list = LFUCache(cfg['INDEX_CACHE_SIZE'])
    tool = BuildIndex(args)
    tool.build_index_main()
