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



def get_cat_fullname(cat):
    """Convert category abbreviation to full name
    
    Arguments:
        cat {[type]} -- [description]
    """