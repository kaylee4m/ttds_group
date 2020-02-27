# ─── CONVERT JSON DATA INTO SQL FOR FAST RETRIVAL ───────────────────────────────
import MySQLdb
import warnings
import urllib.parse
import urllib.request
import re
from global_settings import settings


# from fake_useragent import UserAgent

def getDB(db_config):
    try:
        conn = MySQLdb.connect(host = db_config['host'], user = db_config['user'], passwd = db_config['passwd'],
                               port = db_config['port'], charset = db_config['charset'])
        conn.autocommit(True)
        curr = conn.cursor()
        curr.execute("SET NAMES utf8");
        curr.execute("USE %s" % db_config['db']);
        return conn, curr
    except MySQLdb.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return None, None


def get_doc(doc_id_list):
    """ Get document meta info from database"""
    db_config = {
        'host': '127.0.0.1',
        'user': 'SE',
        'passwd': 'TTDSxfd1920',
        'port': 3306,
        'db': 'ttds',
        'charset': 'utf8'
    }
    meta_dic = {}
    dic = {}
    id = ''
    if 0 == len(doc_id_list):  # check if list is empty
        return meta_dic
    warnings.filterwarnings("ignore")
    conn, curr = getDB(db_config)
    for doc_id in doc_id_list:
        ID = "\'" + doc_id + "\'"
        id = id + ID + ','
    id = id[:-1]
    sql = "SELECT * FROM arxiv WHERE id IN (%s)" % (id)
    if settings['cfg']['DEBUG_PRINT']:
        print(sql)
    try:
        curr.execute(sql)
        results = curr.fetchall()
        for r in results:
            dic['id'] = r[0]
            dic['submitter'] = r[1]
            dic['authors'] = r[2]
            dic['title'] = r[3]
            dic['comments'] = r[4]
            dic['journal-ref'] = r[5]
            dic['doi'] = r[6]
            dic['abstract'] = r[7]
            dic['report-no'] = r[8]
            dic['categories'] = r[9]
            dic['versions'] = r[10]
            dic['pdf_link'] = 'https://arxiv.org/pdf/'+r[0]+'.pdf'
            # try:
            #     num_cite = get_citations(r[3])
            #     if num_cite <= 0:
            #         dic['citations'] = '0'
            #     else:
            #         dic['citations'] = str(num_cite)
            # except Exception as cite_e:
            #     print(cite_e)
            meta_dic[r[0]] = dic
            dic = {}
    except Exception as e:
        print(e)
    conn.close()
    return meta_dic


def get_citations(title):
    """Get the citation numbers from google scholar using scholarly and match the given paper with searched results"""
    num_of_citation = 0
    keyword = title.replace('\n', ' ')  # take out '\n' in titles
    keyword = keyword.replace(' ', '+')  # replace space with +
    # proxy_ip = [{"http":"85.198.250.135:3128"}]
    # ua = UserAgent()
    url = 'https://scholar.google.com/scholar?&hl=en&q=' + keyword + '&btnG=&lr='
    header_dict = {'Host': 'scholar.google.com',
                   # 'User-Agent': ua.random,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Referer': 'https://scholar.google.com/schhp?hl=zh-CN',
                   'Connection': 'keep-alive'}
    req = urllib.request.Request(url = url, headers = header_dict, method = 'GET')
    # proxy = urllib.request.ProxyHandler(proxy_ip[0])
    # opener = urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    # urllib.request.install_opener(opener)
    response = urllib.request.urlopen(req, timeout = 120)
    # if response.status == 200:
    #     print('connect to google scholar succesfully.')
    # else:
    #     print('connection fail!')
    
    data = response.read()
    data = data.decode()
    pattern1 = re.compile(r'\<div class=\"gs_r gs_or gs_scl\".*?data-rp="0".*?\</svg\>\</a\>\</div\>\</div\>\</div\>')
    wholePart = re.search(pattern1, data)
    if wholePart != None:
        wholePart = wholePart.group()  # Find the first result
    else:
        print('Can\'t find this document!', wholePart)
        num_of_citation = -1  # Can't find this document on google scholar, return -1
        return num_of_citation
    # print(wholePart)
    pattern2 = re.compile(r'Cited by (\d*)')
    citation = re.search(pattern2, wholePart)
    if citation != None:
        c = citation.group(1)  # Find the number of citation
        num_of_citation = int(c)
    # print(str(num_of_citation))
    return num_of_citation  # If can't find cited by, return 0
