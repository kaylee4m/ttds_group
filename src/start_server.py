"""
    Communicate with front end?
"""
from flask import Flask, escape, request
from search import Search
from global_settings import settings
from query_suggest import init_ac_fac
from argparse import ArgumentParser
from utils import get_config

app = Flask("Edi Scholar")


def server_args():
    parser = ArgumentParser()
    parser.add_argument("--cfg",
                        default = 'config_server.yaml', required = False)
    
    return parser.parse_args()


def start_server():
    """
    Initialize search engine and autocomplete
    :return:
    """
    args = server_args()
    settings['cfg'] = get_config(args)
    settings['auto_complete'] = init_ac_fac()
    settings['search_engine'] = Search(settings['cfg']).search


@app.route("/")
def deal_request():
    # name = request.args.get("name", "World")
    #
    key = request.args.get('key')
    
    res = settings['search_engine']({
        'keyword': request.args.get('key', ''),
        'pageNum': int(request.args.get('pageNum', 1)),
        'range': "",
        'category': request.args.get('category', '')
    })
    return res


if __name__ == "__main__":
    start_server()
    app.run()
