"""
    Communicate with front end?
"""
from flask import Flask, escape, request
from search import Search
from global_settings import settings
from query_suggest import *
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
    if settings['cfg']['DEBUG_PRINT']:
        print(request.args)
    search_type = request.args.get('request_type', 'search')
    if search_type == 'search':
        start, end = request.args.get('start', 1990), request.args.get('end', 2020)
        res = settings['search_engine']({
            'keyword': request.args.get('key', ''),
            'pageNum': int(request.args.get('pageNum', 1)),
            'range': "%s-%s" % (start, end),
            'category': request.args.get('category', '')
        })
    else:
        # autocomplete, A list of str
        k = request.args.get('key', '')
        res = auto_complete(k)
    return json.dumps(res)

if __name__ == "__main__":
    start_server()
    app.run(port = 8081)
