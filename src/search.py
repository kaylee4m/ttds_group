"""
Core search module
"""
import numpy as np
import pickle
from util import term_to_index
import re
import nltk
from pprint import pprint


class Search:
    def __init__(self, idx_file, stopwords_file):
        with open(idx_file, 'rb') as f:
            self.index = pickle.load(f)
        self.all_doc_id = set(self.index['#HEADLINE'].keys())
        self.all_doc_list = list(self.index['#HEADLINE'].keys())
        self.all_doc_dict = {docID: i for i,
                             docID in enumerate(self.all_doc_list)}
        with open(stopwords_file, 'r') as f:
            self.stopwords = set(f.read().split())
        self.stemmer = nltk.stem.PorterStemmer()

    def parse_query(self, q, query_type=None):
        '''

        :param q:  query
        :param query_type: If we know in advance the type, we dont have to infer its type
        :return:
        '''

        def parse_target(s):
            # May contain NOT
            '''
            :param s:
            :return: tuple; [0] is 0 or 1, 0 for NOT; [1] is a list of preprocessed words.
            '''
            assert type(s) == str
            s = s.strip()
            if s[:3] == 'NOT':
                negation = 0
                s = s[3:]
            else:
                negation = 1
            words = [term_to_index(
                {}, w, 0, 0, self.stopwords, self.stemmer) for w in s.split()]
            words = [w for w in words if w]
            return negation, words

        if query_type == 'r':
            return [parse_target(s) for s in q.split()], query_type
        else:
            if q[0] == '#':
                result = re.split(r"[#(,)]", q)
                return (int(result[1]), parse_target(result[2]), parse_target(result[3])), 'p'
            else:  # boolean
                if ' AND ' in q:
                    tar1, tar2 = [parse_target(s) for s in q.split(' AND ')]
                else:
                    if ' OR ' in q:
                        tar1, tar2 = [parse_target(s) for s in q.split(' OR ')]
                    else:
                        tar1 = parse_target(q)
                        tar2 = parse_target('')
                is_and = 'AND' in q
                return (is_and, tar1, tar2), 'b'

    def make_set(self, var_to_be_set):
        if type(var_to_be_set) is set:
            return var_to_be_set
        elif type(var_to_be_set) == dict:
            return set(var_to_be_set.keys())
        else:
            return set(var_to_be_set)

    def search(self, q, query_type=None, detail=False):
        result, query_type = self.parse_query(q, query_type)
        if query_type == 'r':
            return self.ranked_search(result)
        elif query_type == 'b':
            return self.boolean_search(result)
        elif query_type == 'p':
            return self.proximity_search(result, detail, True)

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

    def proximity_search(self, parsed_q, detail=False, abso=True):
        '''

        :param parsed_q: contains a tuple of 3, which is distance, the first word, and the second word
        :return: a dictionary whose format is the same as term dictionary. result={docId:set(postions)}.
                Here positions means a set of positions of the first word.
                If detail is set to FALSE: return a set of doc IDs.
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
        if not detail:
            result = self.make_set(result)
        return result

    def phrase_search(self, tup, detail=False):
        '''

        :param s: The phrase. You can also input a single word.
            If target contains multiple elements, it is a phrase;
            if it is empty list, it is '' and will return an empty set
            tup[0] 1 or 0 for NOT: tup[1] is the phrase
        :param detail:
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
        if detail:
            return result
        else:
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

    def ranked_search(self, parsed_q, method=''):
        '''

        :param parsed_q:
        :return: tuple of (score, doc)
        '''
        parsed_q = [w[1][0] for w in parsed_q if w[1]]
        tf_matrix = np.zeros([len(self.all_doc_id), len(parsed_q)])
        for i, t in enumerate(parsed_q):
            for d in self.index[t]:
                tf_matrix[self.all_doc_dict[d], i] = len(self.index[t][d])
        df = np.array([len(self.index[t]) for t in parsed_q])
        idf = np.log10(len(self.all_doc_dict) / df)
        not_weight = tf_matrix == 0
        tf_matrix[not_weight] = 1e-10
        log_tf = np.log10(tf_matrix)
        log_tf[not_weight] = -1
        w = (1 + log_tf) * idf
        doc_score = w.sum(axis=1)
        order = np.argsort(doc_score,)[::-1]
        sorted_doc_score = doc_score[order]
        docIDs = np.array(self.all_doc_list)[order]
        return docIDs.tolist(), sorted_doc_score
