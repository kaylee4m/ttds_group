import argparse
import yaml
import json
import os
from global_settings import settings


def createFolder(name, logfile = None):
    name = name.strip().rstrip("/")
    exist = os.path.exists(name)
    if exist:
        # print(name + " already here.")
        pass
    else:
        # print(name + " created.")
        os.makedirs(name)


def get_config(args):
    """
        @return: A dict containing configurations
    """
    cfg_file = args.cfg
    with open(cfg_file, 'r') as f:
        settings['cfg'] = yaml.safe_load(f)
    return settings['cfg']


def args_build_index():
    """
        Set command line arguments for index builder
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg",
                        default = 'config.yaml', required = False)
    
    return parser.parse_args()


def get_sp_term(term, sp = "#"):
    return sp + term


def get_doc_year(doc_id: str) -> str:
    if '/' in doc_id:  # format cat/doct_id:
        _, doc_id_ = doc_id.split('/')
        year = doc_id_[:2]
    else:
        year = doc_id[:2]
    return year


def get_cat_tag(cat, sp = "#"):
    return get_sp_term(cat.upper(), sp)


def get_cat_fullname(cat):
    """Convert category abbreviation to full name

    Arguments:
        cat {[type]} -- [description]
    """
    if not "settings['cat_abbr_to_full']" in globals():
        with open(settings['cfg']['CAT_ABBR_DICT'], 'r') as f:
            con = f.read()
        lines = [line.split() for line in con.strip().split('\n')]
        settings['cat_abbr_to_full'] = {abbr: full for abbr, full in lines}
    return settings['cat_abbr_to_full'][cat]


def get_int_doc_id(doc_id: str):
    if not len(settings['doc_id_2_doc_no']):
        if os.path.exists(settings['cfg']['DOC_ID_2_DOC_NO']):
            with open(settings['cfg']['DOC_ID_2_DOC_NO'], 'r') as f:
                settings['doc_id_2_doc_no'] = json.load(f)
        else:
            # initialize
            settings['doc_id_2_doc_no']['NEXT'] = 0
    return settings['doc_id_2_doc_no'][doc_id]


def get_str_doc_id(doc_id: int) -> str:
    if not len(settings['doc_no_2_doc_id']):
        if not len(settings['doc_id_2_doc_no']) and os.path.exists(
                settings['cfg']['DOC_ID_2_DOC_NO']):  # read from disk
            with open(settings['cfg']['DOC_ID_2_DOC_NO'], 'r') as f:
                settings['doc_id_2_doc_no'] = json.load(f)
        settings['doc_no_2_doc_id'] = {
            v: k for k, v in settings['doc_id_2_doc_no'].items()}
    
    return settings['doc_no_2_doc_id'][doc_id]


def get_doc_numbers():
    """Get the total number of documents
    """
    if not len(settings['doc_id2length']):
        with open(settings['cfg']['DOC_ID_2_DOC_LEN'], 'r') as f:
            settings['doc_id2length'] = json.load(f)
    return len(settings['doc_id2length']) - 2


def get_average_word_count():
    """Get average number of words in documents
    """
    if not len(settings['doc_id2length']):
        with open(settings['cfg']['DOC_ID_2_DOC_LEN'], 'r') as f:
            settings['doc_id2length'] = json.load(f)
    return settings['doc_id2length']['avg']


def get_doc_word_count(doc_id):
    """

    Raises:
        NotImplementedError: [description]

    Returns:
        [type] -- [description]
    """
    if not len(settings['doc_id2length']):
        with open(settings['cfg']['DOC_ID_2_DOC_LEN'], 'r') as f:
            settings['doc_id2length'] = json.load(f)
    return settings['doc_id2length'][doc_id]


def get_index_file_path(key):
    """A key -> a file

    Arguments:
        key {[type]} -- [description]
    """
    return os.path.join(settings['cfg']['INDEX_DIR'],
                        '_'.join([settings['cfg']['INDEX_PREFIX'], '{:03d}'.format(key)]) + '.pkl')


def v_byte_encode(n: int) -> bytearray:
    """Apply variable byte length compression to a number

    Arguments:
        n {int} -- [description]
    """
    b = bytearray()
    while True:
        b.insert(0, n % 128)
        if n < 128:
            break
        n = int(n / 128)
    b[-1] += 128
    return b


def v_byte_decode(bytestream: bytearray) -> int:
    nums = []
    n = 0
    for i, b in enumerate(bytestream):
        if b < 128:
            n = 128 * n + b
        else:
            n = 128 * n + (b - 128)
            nums.append(n)
            n = 0
    return nums


if __name__ == "__main__":
    # Test
    answer1 = [b'\x81',
               b'\x86',
               b'\xff',
               b'\x01\x80',
               b'\x01\x82',
               b'\x01\x1c\xa0', ]
    encode_seq = [1, 6, 127, 128, 130, 20000]
    for i, n in enumerate(encode_seq):
        print(v_byte_encode(n) == answer1[i], v_byte_encode(n), answer1[i])
    # Test Decode
    decoded = v_byte_decode(b''.join(answer1))
    print(decoded == encode_seq, decoded, encode_seq)
