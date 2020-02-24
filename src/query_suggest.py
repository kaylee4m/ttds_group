from fast_autocomplete import autocomplete_factory
from global_settings import settings
import json
from utils import args_build_index, get_config


def init_ac_fac():
    cfg = settings['cfg']
    with open(cfg['UNIGRAM_FILE'], 'r')  as f:
        settings['ngrams'].update(json.load(f))
    with open(cfg['BIGRAM_FILE'], 'r')  as f:
        settings['ngrams'].update(json.load(f))
    with open(cfg['TRIGRAM_FILE'], 'r')  as f:
        settings['ngrams'].update(json.load(f))
    with open('res/all_ngrams.json', 'w') as f:
        json.dump(settings['ngrams'],f)


if __name__ == '__main__':
    args = args_build_index()
    settings['cfg'] = get_config(args)
    init_ac_fac()
