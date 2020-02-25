from argparse import ArgumentParser
import sys
import requests
import  os

def api_args():
    parser = ArgumentParser()
    parser.add_argument('--key', type = str)
    parser.add_argument('--pageNum', type = int)
    parser.add_argument('--category', type = str)
    parser.add_argument('--startYear', type = str)
    parser.add_argument('--endYear', type = str)


if __name__ == '__main__':
    print(sys.argv)
    
    print(os.system('curl http://localhost:5000/?name=dadawkwk'))