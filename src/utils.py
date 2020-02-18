import argparse
import yaml


def get_config(args):
    """
        @return: A dict containing configurations
    """
    cfg_file = args.cfg
    cfg = None
    return cfg
    raise NotImplementedError


def args_build_index():
    """
        Set command line arguments for index builder
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", default='config.yaml', required=False)
    raise NotImplementedError
    return parser.parse_args()
