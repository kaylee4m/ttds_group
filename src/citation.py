'''
Created on 21 Feb 2020

@author: lu_zh
'''
import urllib.parse
import urllib.request
import re

title = 'Calculation of prompt diphoton production cross sections at Tevatron and\n  LHC energies'

def citation(title):
    num_of_citation = 0
    keyword = title.replace('\n','')#take out '\n' in titles
    keyword = keyword.replace(' ','+')#replace space with +
    url='https://scholar.google.com/scholar?&hl=en&q='+keyword+'&btnG=&lr='
    header_dict={'Host': 'scholar.google.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
             'Referer': 'https://scholar.google.com/schhp?hl=zh-CN',
             'Connection': 'keep-alive'}
    req = urllib.request.Request(url=url, headers = header_dict, method = 'GET')
    response = urllib.request.urlopen(req, timeout=120)
    if response.status == 200:
        print('connect to google scholar succesfully.')
    else:
        print('connection fail!')
    
    data=response.read()
    data=data.decode()
    pattern1 = re.compile(r'\<div class=\"gs_r gs_or gs_scl\".*?data-rp="0".*?\</svg\>\</a\>\</div\>\</div\>\</div\>')
    wholePart = re.search(pattern1, data)
    if wholePart != None:
        wholePart = wholePart.group()#Find the first result
    else:
        print('Can\'t find this document!')
        num_of_citation = -1#Can't find this document on google scholar, return -1
        return num_of_citation
    print(wholePart)
    pattern2 = re.compile(r'Cited by (\d*)')
    citation = re.search(pattern2, wholePart)
    if citation != None:
        c = citation.group(1)#Find the number of citation
        num_of_citation = int(c)
    #print(str(num_of_citation))
    return num_of_citation#If can't find cited by, return 0

citation(title)
