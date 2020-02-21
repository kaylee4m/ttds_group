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
from typing import List


class PostingElement:
    """
        Data structure for one element in posting list
    """

    def __init__(self, par, doc_id, author=False):
        self.parent = par
        self.doc_id = doc_id
        self.author = author
        self.positions = []

    def get_term_freq():
        """Term freq of the specific term in this document
        """
        return len(self.positions)

    def add_pos(self, pos):
        """Add one position to positions

        Arguments:
            pos {int} -- [description]
        """

        self.positions.append(pos)

    def __hash__(self):
        return hash(self.parent.term+self.doc_id)


class PostingList:
    """
        Data structure for posting list
    """

    def __init__(self, term):
        self.term = term
        # DONE: TO be decided whether we use a list or a binary tree
        self.doc_ids = {}  # doc_id: idx in list
        self.doc_list = []
        #raise NotImplementedError

    def get_doc_posting(self, article, authors):
        """If a doc is recorded, return it; if not, create the postingElement for it and return it

        Arguments:
            article {dict} -- [description]

        Returns:
            [type] -- [description]
        """
        doc_id = article['id']
        if doc_id not in self.doc_ids:
            is_author = self.term in authors
            # ideally doc id is inserted ascendingly
            self.doc_list.append(PostingElement(
                self, doc_id,
                author=is_author))
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
        id_list = [element.doc_id for element in self.doc_list]
        return id_list

    def get_postings(self, year_range: str = "") -> List[PostingElement]:
        """
            Return all postings
            if year range is specified as "2019-2020" only return those published in these years
        """
        if len(year_range) == 0:
            return self.doc_list
        else:
            condition = [i for i in range(
                int(year_range[2:4]), int(year_range[7:]))]

            filtered_posting = [element for element in self.doc_list if int(
                element.doc_id[:2]) in condition]
            return filtered_posting

    def get_doc_freq(self):
        """Get document frequency of this term
        """
        raise NotImplementedError
        return 0

    def __str__(self):
        return ""


def get_term_key(cfg, term):
    """
        convert a term into key. Terms with the same key will be saved into the same file.
        Used to find posting list group in cached_posting_list.
        See Index Storage and Compression section in report.
    """
    obj = hashlib.md5()
    obj.update(term.encode("utf-8"))
    key = int(obj.hexdigest(), 16) % cfg['NUM_INDEX_FILES']
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
        pl_object = json.loads(js)  # load posting list object using json
    pl_group = pl_object.decode()
    return pl_group


def get_posting_list(cfg, term: str, index_dir) -> PostingList:
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
    key = get_term_key(cfg, term)
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


def save_posting_list_group(key, pl_group, index_dir):
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
        authors = preprocessing(stemmer, " ".join(
            article['authors']), stop_words)

        # TODO: combine title, author and content
        # use get_doc_year to get year from doc id,
        # before add year into index, make it special by using get_sp_term. "08" -> "#08"
        # use get_cat_tag to get special term for category
        content = nltk.word_tokenize(title + abstract)
        cleaned_words = preprocessing(content, stop_words, stemmer)
        for pos, word in enumerate(cleaned_words):
            pl: PostingList = get_posting_list(
                self.cfg, word, self.cfg['INDEX_DIR'])
            doc_posting: PostingElement = pl.get_doc_posting(article)
            doc_posting.add_pos(pos)
        # TODO: build index for category?
        # Note: Use both large and small category as index. Eg. a paper might be categorized as cs.AI
        # we need to build 2 indices: #CS and #CS.AI
        raise NotImplementedError

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
            save_posting_list_group(k, pl, self.cfg['INDEX_DIR'])

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
