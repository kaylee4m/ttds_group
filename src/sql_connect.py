# ─── CONVERT JSON DATA INTO SQL FOR FAST RETRIVAL ───────────────────────────────
import scholarly
import MySQLdb
import warnings
import urllib.parse
import urllib.request
import re


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


def get_doc(doc_id):
    """ Get document meta info from database"""
    db_config = {
        'host': '127.0.0.1',
        'user': 'SE',
        'passwd': 'TTDSxfd1920',
        'port': 3306,
        'db': 'ttds',
        'charset': 'utf8'
    }
    dic = {}
    warnings.filterwarnings("ignore")
    conn, curr = getDB(db_config)
    id = "\'" + doc_id + "\'"
    sql = "SELECT * FROM arxiv WHERE id = %s" % (id)
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
    except:
        print('Error:unable to find the data!')
    conn.close()
    return dic


def get_citations(article: dict):
    """Get the citation numbers from google scholar using scholarly and match the given paper with searched results"""
    title = article['title']
    num_of_citation = 0
    keyword = title.replace('\n', '')  # take out '\n' in titles
    keyword = keyword.replace(' ', '+')  # replace space with +
    url = 'https://scholar.google.com/scholar?&hl=en&q=' + keyword + '&btnG=&lr='
    header_dict = {'Host': 'scholar.google.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Referer': 'https://scholar.google.com/schhp?hl=zh-CN',
                   'Connection': 'keep-alive'}
    req = urllib.request.Request(url = url, headers = header_dict, method = 'GET')
    response = urllib.request.urlopen(req, timeout = 120)
    if response.status == 200:
        print('connect to google scholar succesfully.')
    else:
        print('connection fail!')
    
    data = response.read()
    data = data.decode()
    pattern1 = re.compile(r'\<div class=\"gs_r gs_or gs_scl\".*?data-rp="0".*?\</svg\>\</a\>\</div\>\</div\>\</div\>')
    wholePart = re.search(pattern1, data)
    if wholePart != None:
        wholePart = wholePart.group()  # Find the first result
    else:
        print('Can\'t find this document!')
        num_of_citation = -1  # Can't find this document on google scholar, return -1
        return num_of_citation
    print(wholePart)
    pattern2 = re.compile(r'Cited by (\d*)')
    citation = re.search(pattern2, wholePart)
    if citation != None:
        c = citation.group(1)  # Find the number of citation
        num_of_citation = int(c)
    # print(str(num_of_citation))
    return num_of_citation  # If can't find cited by, return 0
