import argparse
import yaml


def get_config(args):
    """
        @return: A dict containing configurations
    """
    cfg_file = args.cfg
    with open(cfg_file, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg


def args_build_index():
    """
        Set command line arguments for index builder
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", default='config.yaml', required=False)

    return parser.parse_args()


def get_sp_term(term, sp="#"):
    return sp+term


def get_doc_year(doc_id: str) -> str:
    if '/' in doc_id:  # format cat/doct_id:
        _, doc_id_ = doc_id.split('/')
        year = doc_id_[:2]
    else:
        year = doc_id[:2]
    return year


def get_cat_tag(cat, sp="#"):
    return get_sp_term(cat.upper(), sp)


def get_cat_fullname(cfg, cat):
    """Convert category abbreviation to full name

    Arguments:
        cat {[type]} -- [description]
    """
    if not "cat_abbr_to_full" in globals():
        with open(cfg['CAT_ABBR_DICT'], 'r') as f:
            con = f.read()
        global cat_abbr_to_full
        lines = [line.split() for line in con.strip().split('\n')]
        cat_abbr_to_full = {abbr: full for abbr, full in lines}
    global cat_abbr_to_full
    return cat_abbr_to_full[cat]


def get_average_word_count():
    """Get average number of words in documents
    """
    raise NotImplementedError


def get_doc_numbers():
    """Get the number of documents
    """
    raise NotImplementedError


def get_doc_word_count(doc_id):
    """

    Raises:
        NotImplementedError: [description]

    Returns:
        [type] -- [description]
    """
    global doc_word_count
    if 'doc_word_count' in globals():
        return doc_word_count[doc_id]
    else:
        # read from disk

        raise NotImplementedError
