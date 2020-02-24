import gzip
import json
import pickle
import tqdm
import nltk
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from utils import *
import hashlib
from cachetools import *
from typing import List, Dict
from global_settings import settings
import os
import contractions
import multiprocessing
import threading


class PostingElement:
    """
        Data structure for one element in posting list
    """

    def __init__(self, par, doc_id, author=False):
        self.parent = par
        self.doc_id = doc_id
        self.author = author
        self.num_pos = 0
        self.positions = []

    def get_term_freq(self):
        """Term freq of the specific term in this document
        """
        return len(self.positions)

    def get_doc_year(self):
        return int(self.doc_id[:2])

    def add_pos(self, pos):
        """Add one position to positions

        Arguments:
            pos {int} -- [description]
        """

        self.num_pos += 1
        self.positions.append(pos)

    def __hash__(self):
        return hash(self.parent.term + self.doc_id)

    def __str__(self):
        return "%s-%s" % (self.parent.term, self.doc_id)


class PostingList:
    """
        Data structure for posting list
    """

    def __init__(self, term):
        self.term = term
        # DONE: TO be decided whether we use a list or a binary tree
        self.doc_ids = {}  # doc_id: idx in list
        self.doc_list = []
        # raise NotImplementedError

    def get_doc_posting(self, article, authors) -> PostingElement:
        """If a doc is recorded, return it; if not, create the postingElement for it and return it

        Arguments:
            article {dict} -- [description]

        Returns:
            [type] -- [description]
        """
        self.doc_id = article['id']
        if self.doc_id not in self.doc_ids:
            is_author = self.term in authors
            self.add_doc_ele(PostingElement(
                self, self.doc_id, author=is_author))
        return self.doc_list[self.doc_ids[self.doc_id]]

    def add_doc_ele(self, doc_ele: PostingElement):
        # ideally doc id is inserted ascendingly
        doc_ele.parent = self
        self.doc_list.append(doc_ele)
        self.doc_ids[doc_ele.doc_id] = len(self.doc_list) - 1

    def get_posting_by_docid(self, doc_id):
        if doc_id not in self.doc_ids:
            return None
        return self.doc_list[self.doc_ids[doc_id]]

    def encode(self):
        """
            Apply index compression.
            Format: doc_id/d_gap, is_author, num_positions, positions
            @return: byte array to save to disk
        """
        doc_no_list = sorted([get_int_doc_id(doc_id)
                              for doc_id in self.doc_ids])
        byte_seq = bytearray()
        prev_doc_no = 0
        for d_no in doc_no_list:
            d_gap = d_no - prev_doc_no
            doc_element: PostingElement = self.get_posting_by_docid(
                get_str_doc_id(d_no))
            num_positions = doc_element.get_term_freq()
            all_info = [d_gap, int(doc_element.author),
                        num_positions] + doc_element.positions
            byte_seq.extend(b''.join([v_byte_encode(i) for i in all_info]))
            prev_doc_no = d_no

        return byte_seq

    @staticmethod
    def decode(term, byte_seq):
        """
            Decode index compression.
            @return: PostingList object
        """
        all_info = v_byte_decode(byte_seq)
        pl = PostingList(term)
        i = 0
        doc_no = 0
        while i < len(all_info):
            doc_no += all_info[i]
            doc_id = get_str_doc_id(doc_no)
            i += 1
            is_author = all_info[i]
            i += 1
            num_positions = all_info[i]
            i += 1
            doc_ele: PostingElement = PostingElement(pl, doc_id, is_author)
            for j in range(num_positions):
                doc_ele.add_pos(all_info[i])
                i += 1
            pl.add_doc_ele(doc_ele)
        return pl

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
        return len(self.doc_list)


def get_term_key(term):
    """
        convert a term into key. Terms with the same key will be saved into the same file.
        Used to find posting list group in settings['cached_posting_list'].
        See Index Storage and Compression section in report.
    """
    obj = hashlib.md5()
    obj.update(term.encode("utf-8"))
    key_2 = int(obj.hexdigest(), 16) % settings['cfg']['NUM_INDEX_FILES']
    count = get_word_occurences(term)
    magnitude = 0
    while int(count/(10**magnitude)):
        magnitude += 1
    key = magnitude*settings['cfg']['NUM_INDEX_FILES'] + key_2
    return key


def load_pl_group_by_term(term):
    """
        Find the index file associated with this key.
        A file contains many posting lists (each associated with one term)
    """
    # DONE load from disk
    #  decode  with PostingList.decode()
    # and return group of pls
    key = get_term_key(term)
    path = get_index_file_path(key)
    if os.path.exists(path):
        # load from disk
        with open(path, 'rb') as dictfile:
            byte_group = pickle.load(dictfile)
        pl_group = {k: PostingList.decode(k, v) for k, v in byte_group.items()}

        if settings['cfg']['DEBUG_PRINT']:
            print("Load  %s." % (get_index_file_path(key)))

    else:
        # create a new group
        pl_group = {term: PostingList(term)}
    return pl_group


def get_posting_list(term: str) -> PostingList:
    """        Get a posting list using term as the key


    Arguments:
        term {[type]} -- [description]

    Returns:
        posting_list: PostingList -- The posting_list for the term.
                         Return None if not presented in index 
    """
    key = get_term_key(term)
    if key in settings['cached_posting_list']:
        # DONE: load
        pl_group = settings['cached_posting_list'][key]
    else:
        #  add to cache
        # save to disk if some cached posting is discarded
        while len(settings['cached_posting_list']) >= settings['cfg']['INDEX_CACHE_SIZE']:
            poped_key, poped_pl_group = settings['cached_posting_list'].popitem(
            )
            # threading.Thread(target = save_posting_list_group, args = (poped_key, poped_pl_group)).start()
            save_posting_list_group(poped_key, poped_pl_group)
        pl_group = load_pl_group_by_term(term)
        settings['cached_posting_list'][key] = pl_group
        # actually, load by key, so there might be prob that this term is not in the dict
    if not term in pl_group:
        posting_list = PostingList(term)
        pl_group[term] = posting_list
    else:
        posting_list = pl_group[term]
    return posting_list


def save_posting_list_group(key: str, pl_group: Dict):
    """Save a posting list group to disk
        # TODO Remember to save **asynchronously** to disk
    Arguments:
        key {str} -- [description]
        pl_group {Dict} -- [description]
    """
    byte_group = {k: v.encode() for k, v in pl_group.items()}
    with open(get_index_file_path(key), 'wb') as file:
        pickle.dump(byte_group, file)
        if settings['cfg']['DEBUG_PRINT']:
            print("Save  %s." % (get_index_file_path(key)))


def preprocessing(stemmer, content, stop_words):
    # TODO: split at '-'
    # TODO: Dont filter out words with punctuations, deal with it
    cleaned_list = []
    pattern = '[^a-zA-Z0-9\-\ ]'
    content = contractions.fix(content, slang=False)
    content_str = re.sub(pattern, ' ', content).lower()
    tokens_list = nltk.word_tokenize(content_str)
    for token in tokens_list:
        if token not in stop_words:
            token = stemmer.stem(token)
            cleaned_list.append(token)
    return cleaned_list


class BuildIndex:
    def __init__(self, cfg):
        self.cfg = cfg

    def Doc(self, id, term_freq):  # remove unused function?
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
        author_processed = preprocessing(stemmer, authors, stop_words)
        # DONE: combine title, author and content %finished
        # use get_doc_year to get year from doc id,
        # before add year into index, make it special by using get_sp_term. "08" -> "#08"
        # use get_cat_tag to get special term for category

        content = authors + title + abstract
        cleaned_words = preprocessing(stemmer, content, stop_words)

        for pos, word in enumerate(cleaned_words):
            pl: PostingList = get_posting_list(word)
            doc_posting: PostingElement = pl.get_doc_posting(
                article, author_processed)
            doc_posting.add_pos(pos)

        # DONE: build mapping from string doc id to int doc id
        doc_length = len(nltk.word_tokenize(abstract))
        doc_id2length[doc_id] = doc_length
        doc_id2length['all'] += doc_length

        # DONE: build index for category?
        # Note: Use both large and small category as index. Eg. a paper might be categorized as cs.AI
        # we need to build 2 indices: #CS and #CS.AI

        for cat in categories[0].split():
            larger_cat = cat.split('.')[0]
            pl: PostingList = get_posting_list(get_cat_tag(larger_cat))
            pl.get_doc_posting(article, [])  # if in it
            pl: PostingList = get_posting_list(get_cat_tag(cat))
            pl.get_doc_posting(article, [])

    def build_index(self):
        """
            To build index using All data
        """

        # TODO Only need to download once, please check this
        doc_num = get_int_doc_id('NEXT')  # init doc_id_2_doc_no
        # nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))
        ps = PorterStemmer()
        with gzip.open(self.cfg['ALL_DATA'], 'rt', encoding='utf-8') as fin:
            for i, line in enumerate(tqdm.tqdm(fin.readlines())):
                # if i > 1000: break
                article = json.loads(line)
                # put this after processing, because we need to
                if article['id'] not in settings['doc_id_2_doc_no']:
                    doc_num = get_int_doc_id('NEXT')
                    settings['doc_id_2_doc_no'][article['id']] = doc_num
                    settings['doc_no_2_doc_id'][doc_num] = article['id']
                    settings['doc_id_2_doc_no']['NEXT'] += 1
                self.process_one_article(article, stop_words, ps)

    def update_index(self, gz_file, index_dir):
        """
            To update current index using new data. 
            Expect: All doc id are new 
        """
        raise NotImplementedError

    def build_index_main(self):
        # DONE
        self.build_index()
        # save all the rest in cache
        for k, pl_group in settings['cached_posting_list'].items():
            save_posting_list_group(k, pl_group)

    def update_index_main(self, args):
        pass


if __name__ == "__main__":
    doc_id2length = defaultdict(int)

    args = args_build_index()
    settings['cfg'] = get_config(args)
    createFolder(settings['cfg']['INDEX_DIR'])
    # dict of group of posting lists
    settings['cached_posting_list'] = LFUCache(
        settings['cfg']['INDEX_CACHE_SIZE'])
    tool = BuildIndex(settings['cfg'])
    tool.build_index_main()

    # save the settings['doc_id_2_doc_no'] dict as json file
    js = json.dumps(settings['doc_id_2_doc_no'])
    with open(settings['cfg']['DOC_ID_2_DOC_NO'], 'w') as file:
        file.write(js)

    total_len = 0
    doc_id2length['avg'] = 0
    # -2 for all and avg
    doc_id2length['avg'] = int(doc_id2length['all'] / (len(doc_id2length) - 2))
    # save the doc_id2length dict as json file
    js = json.dumps(doc_id2length)
    with open(settings['cfg']['DOC_ID_2_DOC_LEN'], 'w') as file:
        file.write(js)
