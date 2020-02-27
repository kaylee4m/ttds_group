from fast_autocomplete import autocomplete_factory
from global_settings import settings
import json
from utils import args_build_index, get_config
import time


def init_ac_fac():
    cfg = settings['cfg']
    # with open(cfg['UNIGRAM_FILE'], 'r')  as f:
    #     settings['ngrams'].update(json.load(f))
    # with open(cfg['BIGRAM_FILE'], 'r')  as f:
    #     settings['ngrams'].update(json.load(f))
    # with open(cfg['TRIGRAM_FILE'], 'r')  as f:
    #     settings['ngrams'].update(json.load(f))
    # with open('res/all_ngrams.json', 'w') as f:
    #     json.dump(settings['ngrams'],f)
    #
    # with open(cfg['BIGRAM_FILE_FULL'], 'r')  as f:
    #     settings['unigram'].update(json.load(f))
    content_files = {
        'words': {
            'filepath': cfg[cfg['AC_DIC']],
            'compress': True  # means compress the graph data in memory
        }
    }
    autocomplete = autocomplete_factory(content_files = content_files)
    ac = lambda word, s: autocomplete.search(word, size = s)
    return ac


def auto_complete(words):
    words = words.split()
    keep = min(3, len(words))
    words = ' '.join(words[-keep:])
    results = settings['auto_complete'](words,  settings['cfg']['SUGGESTION_NUMBER'])
    results = [sugg[0] for sugg in results]
    return results


if __name__ == '__main__':
    args = args_build_index()
    settings['cfg'] = get_config(args)
    ac = init_ac_fac()
    start = time.time()
    print(ac("thermo", 10))
    print("Time %.4f" % (time.time() - start))
    start = time.time()
    print(ac("graphics", 10))
    print("Time %.4f" % (time.time() - start))
    
    start = time.time()
    print(ac("chris", 10))
    print("Time %.4f" % (time.time() - start))
