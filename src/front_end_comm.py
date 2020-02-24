"""
    Communicate with front end?
"""

import flask
from search import Search
from global_settings import settings
from query_suggest import init_ac_fac


def start_server():
    """
    Initialize search engine and autocomplete
    :return:
    """
    settings['auto_complete'] = init_ac_fac()
    settings['search_engine'] = Search().search


def deal_request():
    pass


if __name__ == "__main__":
    pass
