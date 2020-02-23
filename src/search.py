"""
Core search module
TODO Reimplement all methods for large-scale document collection,  
expect at least 10k entries for a keyword
"""
import numpy as np
from arxiv_indexing import *
from sql_connect import *
from typing import List, Set
from functools import reduce
from cachetools import LRUCache
from global_settings import settings


class Search:
    def __init__(self, cfg):
        self.cfg = cfg
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.index = []
        self.stemmer = nltk.stem.PorterStemmer()
        self.searched_results = LRUCache(
            self.cfg['SEARCH_CACHE_SIZE'])  # cached dictionary
    
    def search(self, q, query_type = None, ):
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
            # TODO see if prepro is used correctly
            words = preprocessing(self.stemmer, q['keyword'].split(), self.stopwords)
            ori_pls = [get_posting_list(w)
                       for w in words]
            total_docs = get_doc_numbers()
            df = [p.get_doc_freq() for p in ori_pls]
            pls = [p.get_postings(q['range']) for p in ori_pls]
            # DONE: Filter categories. pls should be List[List[PostingElement]]
            # Assume categories are abbreviation
            if q['category']:
                cats = [get_cat_tag(c.strip(',')) for c in q["category"].split(
                    self.cfg['CAT_SPLIT_SYMB'])]
                cat_pls = [get_posting_list(c).get_postings(
                    q['range']) for c in cats]
                cat_pl_set: Set[PostingElement] = reduce(set.union, [set(p) for p in cat_pls])
                pls = self.boolean_search(pls, cat_pl_set)
                # if a term does not appear in a specific category, no need to search among these
                df = [df[i] for i, p in enumerate(pls) if p]
                pls = [p[i] for i, p in enumerate(pls) if p]
            df = np.array(df)
            idf = np.log10((total_docs - df + .5) / (df + .5))
            # Search the rest posting lists
            doc_ids = self.ranked_search(pls, idf)
            results = get_docs(doc_ids)
            # split results into pages
            i = 0
            split_results = []
            while i < len(results):
                end = min(i + self.cfg['SEARCH_RESULTS_PER_PAGE'], len(results))
                split_results.append(results[i:end])
                i += self.cfg['SEARCH_RESULTS_PER_PAGE']
            self.searched_results[key] = split_results
        return self.searched_results[key][q['pageNum']]
    
    def boolean_search(self, candidate: List[List[PostingElement]],
                       must_in: Set[PostingElement]) -> List[List[PostingElement]]:
        """Cast boolean search on candidate. Filter our those not in must_in
        Arguments:
            candidate {PostingList} -- [description]
            must_in {PostingList} --  

        Returns:
            List[List[PostingElement]] -- [description]
        """
        docs_must_in = set([d.doc_id for d in must_in])
        result = []
        for pl in candidate:
            result.append([ele for ele in pl if ele.doc_id in docs_must_in])
        return candidate
    
    def get_BM25_score(self, posting_lists: List[List[PostingElement]], doc_id_to_idx, idf):
        num_terms = len(posting_lists)
        num_docs = len(doc_id_to_idx)
        avg_len = get_average_word_count()
        doc_len = np.zeros(num_docs)
        for doc_id, idx in doc_id_to_idx.items():
            doc_len[idx] = get_doc_word_count(
                get_doc_word_count(doc_id)) / avg_len
        doc_len = np.array(doc_len)
        k = self.cfg['BM25_COEFF']
        tf_matrix = np.zeros([num_docs, num_terms])
        for j, p in enumerate(posting_lists):
            for d in p:
                i = doc_id_to_idx[d.doc_id]
                tf_matrix[i, j] = d.get_term_freq()
        # TODO check whether this impl is right
        tf_matrix = tf_matrix / (tf_matrix + .5 + k * doc_len[:, np.ones(num_terms)])
        
        weights = tf_matrix * idf
        weights = weights.sum(axis = 1)
        
        return weights
    
    def ranked_search(self, posting_lists: List[List[PostingElement]], idf, method = 'BM25'):
        '''

        :param posting_lists:
        :return: tuple of (score, doc)
        '''
        # get all doc ids from postings
        # get scores for each document
        # sort
        all_doc_ids = sorted(
            list(set([d.doc_id for p in posting_lists for d in p])))
        doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(all_doc_ids)}
        if doc_id_to_idx:
            if method == 'BM25':
                doc_score = self.get_BM25_score(posting_lists, doc_id_to_idx, idf)
            else:
                doc_score = self.get_BM25_score(posting_lists, doc_id_to_idx, idf)
            keep = min(len(all_doc_ids), self.cfg["SEARCH_RESULTS_KEEP"])
            order = np.argsort(doc_score)[::-1][:keep]
            order = order.tolist()
        else:
            order = []
        
        return order


if __name__ == "__main__":
    args = args_build_index()
    settings['cfg'] = get_config(args)
    s = Search(settings['cfg'])
    res = s.search({
        'keyword': 'mage',
        'pageNum': 2,
        'range': "",
        'category': ""
    })
    print(res)
