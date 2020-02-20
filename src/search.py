"""
Core search module
TODO Reimplement all methods for large-scale document collection,  
expect at least 10k entries for a keyword
"""
import numpy as np
import pickle
from util import term_to_index
import re
import nltk
from pprint import pprint
from arxiv_indexing import *
from sql_connect import *
from typing import List
from functools import reduce
from cachetools import LRUCache


class Search:
    def __init__(self, cfg):
        self.cfg = cfg
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.index = []
        self.stemmer = nltk.stem.PorterStemmer()
        self.cat_dict = {}
        with open(cfg['CAT_ABBR_DICT'], 'r') as f:
            for line in f.readlines():
                abbr, full = line.strip().split()
                self.cat_dict[abbr] = full
        self.searched_results = LRUCache(
            self.cfg['SEARCH_CACHE_SIZE'])  # cached dictionary

    def search(self, q, query_type=None,):
        """Search by query

        Arguments:
            :param q:  query. dictionary. keys are "keyword", "pageNum", "range"(years), "category"

        Keyword Arguments:
            query_type {[type]} -- [description] (default: {None})


        Returns:
            result -- a generator of result list
        """
        key = q['keyword'] + str(q['range']) + str(q['category'])
        if key not in self.searched_results:
            words = preprocessing(self.stemmer, q['keyword'], self.stopwords)
            pls = [get_posting_list(w, self.cfg['INDEX_DIR']) for w in words]
            total_docs = get_doc_numbers()
            df = np.log10(np.array([
                p.get_doc_freq() for p in pls
            ]))
            idf = np.log10((total_docs-df+.5)/(df+.5))
            # TODO filter out years
            pls = [get_posting_list(w, self.cfg['INDEX_DIR']) for w in words]
            
            # TODO: Filter categories. pls should be List[List[PostingElement]]

            doc_ids = self.ranked_search(pls, idf)
            results = get_docs(doc_ids)
            # split results into pages
            i = 0
            split_results = []
            while i < len(results):
                end = min(i+self.cfg['SEARCH_RESULTS_PER_PAGE'], len(results))
                split_results.append(results[i:end])
                i += self.cfg['SEARCH_RESULTS_PER_PAGE']
            self.searched_results[key] = split_results
        return self.searched_results[key][q['pageNum']]

    def make_set(self, var_to_be_set):
        if type(var_to_be_set) is set:
            return var_to_be_set
        elif type(var_to_be_set) == dict:
            return set(var_to_be_set.keys())
        else:
            return set(var_to_be_set)

    def single_search(self, target):
        '''

        :param target: single words' dict
        :return:
        '''
        is_inclusive, word = target
        word = word[0]
        if word not in self.index:
            raise KeyError("Target %s must be in the term list." % target)
        else:
            return self.index[word]
            # return self.all_doc_id - set(self.index[word].keys())

    def proximity_search(self, parsed_q, abso=True):
        '''

        :param parsed_q: contains a tuple of 3, which is distance, the first word, and the second word
        :return: a dictionary whose format is the same as term dictionary. result={docId:set(postions)}.
                Here positions means a set of positions of the first word.
        '''
        dist, tar1, tar2 = parsed_q
        docs1 = self.single_search(tar1)
        docs2 = self.single_search(tar2)
        assert type(docs1) == type(docs2) == dict
        result = {}
        for d, pos_list1 in docs1.items():
            if d in docs2:
                pos_list2 = set(docs2[d])
                for p1 in pos_list1:
                    for p2 in pos_list2:
                        if (0 < abs(p2 - p1) <= dist and abso) or (0 < p2 - p1 <= dist and not abso):
                            result.setdefault(d, set()).add((p1, p2))
        return result

    def phrase_search(self, tup):
        '''

        :param s: The phrase. You can also input a single word.
            If target contains multiple elements, it is a phrase;
            if it is empty list, it is '' and will return an empty set
            tup[0] 1 or 0 for NOT: tup[1] is the phrase

        :return: Return the set of docID it resides in
        '''
        is_include, word = tup
        if len(word) == 1:
            result = self.single_search(tup)
        elif len(word) > 1:
            first_and_second = self.proximity_search(
                (1, (1, [word[0]]), (1, [word[1]])), abso=False)
            result = first_and_second
        else:
            result = {}
        if is_include:
            return self.make_set(result)
        else:
            return self.all_doc_id - self.make_set(result)

    def boolean_search(self, parsed_q):
        is_and, tar1, tar2 = parsed_q
        docs1 = self.make_set(self.phrase_search(tar1))
        docs2 = self.make_set(self.phrase_search(tar2))
        if is_and:
            result = docs1 & docs2
        else:
            result = docs1 | docs2
        result = sorted(list(result))
        return result

    def get_BM25_score(self, posting_lists:  List[List[PostingElement]],  doc_id_to_idx, idf):
        num_terms = len(posting_lists)
        num_docs = len(doc_id_to_idx)
        avg_len = get_average_word_count()
        doc_len = np.zeros(num_docs)
        for doc_id, idx in doc_id_to_idx.items():
            doc_len[idx] = get_doc_word_count(
                get_doc_word_count[doc_id])/avg_len
        doc_len = np.array(doc_len)
        k = self.cfg['BM25_COEFF']
        # TO be checked
        tf_matrix = np.zeros([num_docs, num_terms])
        for j, p in enumerate(posting_lists):
            for d in p:
                i = doc_id_to_idx[d.doc_id]
                tf_matrix[i, j] = d.get_term_freq()
        # TODO check whether this impl is right
        tf_matrix = tf_matrix / (tf_matrix+.5+k*doc_len[:, np.ones(num_terms)])

        weights = tf_matrix*idf
        weights = weights.sum(axis=1)

        return weights

    def ranked_search(self, posting_lists: List[List[PostingElement]], idf, method='BM25'):
        '''

        :param posting_lists:
        :return: tuple of (score, doc)
        '''
        # get all doc ids from postings
        # get scores for each document
        # sort
        all_doc_ids = sorted(
            list(set([d.doc_id for d in p for p in posting_lists])))
        doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(all_doc_ids)}
        if method == 'BM25':
            doc_score = self.get_BM25_score(posting_lists, doc_id_to_idx, idf)
        else:
            doc_score = self.get_BM25_score(posting_lists, doc_id_to_idx, idf)

        # for i, t in enumerate(parsed_q):
        #     for d in self.index[t]:
        #         tf_matrix[self.all_doc_dict[d], i] = len(self.index[t][d])
        # df = np.array([len(self.index[t]) for t in parsed_q])
        # idf = np.log10(len(self.all_doc_dict) / df)
        # not_weight = tf_matrix == 0
        # tf_matrix[not_weight] = 1e-10
        # log_tf = np.log10(tf_matrix)
        # log_tf[not_weight] = -1
        # w = (1 + log_tf) * idf
        # doc_score = w.sum(axis=1)
        keep = min(len(all_doc_ids), self.cfg["SEARCH_RESULTS_KEEP"])
        order = np.argsort(doc_score)[::-1][:keep]

        return order.tolist()


if __name__ == "__main__":
    pass
