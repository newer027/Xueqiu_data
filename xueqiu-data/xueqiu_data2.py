# -*- coding: utf-8 -*-

import json
from operator import itemgetter
import re
import urllib.request
from bs4 import BeautifulSoup  # $ pip install beautifulsoup4
from bson import json_util
#html='https://xueqiu.com/P/ZH701073'
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import time
import datetime
import pandas

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 
cl = MongoClient()
coll = cl["local"]["test2"]
projects = {}
ZHs0={}
ZHs1={}
cookie = 's=7l12apugrb; xq_a_token=09edd344afac6eb03a03073c5afae983a81c9bdf; xqat=09edd344afac6eb03a03073c5afae983a81c9bdf; xq_r_token=7a735457503c14b65ca8a050828f0a9cb1345294; xq_is_login=1; u=1180102135; xq_token_expire=Thu%20Dec%2022%202016%2011%3A54%3A00%20GMT%2B0800%20(CST); bid=45efaa8643ba70c7f4357d0930ff99d4_iw042v36; Hm_lvt_1db88642e346389874251b5a1eded6e3=1478268495,1478268632,1478268834,1478309559; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1480218848'

def prof(url_ap0):
    url = 'https://xueqiu.com/cubes/rebalancing/history.json?cube_symbol='+url_ap0+'&count=20&page=1'
    req = urllib.request.Request(url,headers = {#'X-Requested-With': 'XMLHttpRequest',
           #'Referer': 'http://xueqiu.com/p/ZH010389',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
           #'Host': 'xueqiu.com',
           #'Connection':'keep-alive',
           #'Accept':'*/*',
           'cookie':cookie
           })
    html = urllib.request.urlopen(req).read().decode('utf-8')
    #print(html)
    data = json.loads(html)

    for i in range (len(data['list'])):
        #localtime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(data['list'][i]['updated_at'] / 1000))
        #print('\n'+"    ************************")
        #print (url_ap0+"  Transaction time:", localtime)
        for j in range(len(data['list'][i]['rebalancing_histories'])):
            if pandas.isnull(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted']):
                data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] = str(0)
            else:
                data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] = str(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'])
            if pandas.isnull(data['list'][i]['rebalancing_histories'][j]['target_weight']):
                data['list'][i]['rebalancing_histories'][j]['target_weight'] = str(0)
            else:
                data['list'][i]['rebalancing_histories'][j]['target_weight'] = str(data['list'][i]['rebalancing_histories'][j]['target_weight'])
            #print(data['list'][i]['rebalancing_histories'][j]['stock_name'] + '   持仓变化:  '+ data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] + '% to ' + data['list'][i]['rebalancing_histories'][j]['target_weight'] + '%')
        #print(stockName +" "+url_ap0 + "    - - - - -\t - - - - -")
        #print(com['stocks'][o]['name']+"\t净值:"+com['stocks'][o]['net_value']+" 月收益:"+com['stocks'][o]['monthly_gain']+"%")
        #printline += ("Transaction time:\t", localtime)
    try:
        for i in range(len(data['list'])):
            localtime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(data['list'][i]['updated_at'] / 1000))
            if (time.time() - (data['list'][i]['updated_at'] / 1000)) < 86400*20:
                for j in range(len(data['list'][i]['rebalancing_histories'])):
                    ZHs1[j-data['list'][i]['updated_at']]=(localtime,url_ap0,ZHs0[url_ap0],data['list'][i]['rebalancing_histories'][j]['stock_name'] + ': '+ data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] + '% ' + ("⬆" if float(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'])<float(data['list'][i]['rebalancing_histories'][j]['target_weight']) else "⇩") + ' '+ data['list'][i]['rebalancing_histories'][j]['target_weight'] + '%')
    except:
        print("exception occured")


def get_xueqiu_hold(url):
    req = urllib.request.Request(url,headers = {#'X-Requested-With': 'XMLHttpRequest',
               #'Referer': 'http://xueqiu.com/p/ZH010389',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
               #'Host': 'xueqiu.com',
               #'Connection':'keep-alive',
               #'Accept':'*/*',
               'cookie':cookie
               })
    soup = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(soup, 'lxml')
    script = soup.find('script', text=re.compile('SNB\.cubeInfo'))
    json_text = re.search(r'^\s*SNB\.cubeInfo\s*=\s*({.*?})\s*;\s*$',
                      script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    data = json.loads(json_text)
    #print(data["view_rebalancing"]["holdings"][0]['stock_name'])
    #print(data["view_rebalancing"]["holdings"][0]['weight'])
    #assert data['activity']['type'] == 'read'
    for d in data["view_rebalancing"]["holdings"]:
        if d['stock_name'] in projects.keys():
            projects[d['stock_name']] += d['weight']            
        else:
            projects[d['stock_name']]= d['weight']
    """
    for d in data["view_rebalancing"]["holdings"]:
        i = coll.find({'stock_name':d['stock_name']})
        if(i):
            coll.update({'stock_name':d['stock_name']}, {'weight':d['weight']})      
        else:
            coll.update({'stock_name':d['stock_name']}, d, True)
    """
    

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

"""
@app.route('/start', methods=['POST'])
def post_url():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'https://' not in url[:8]:
        url = 'https://' + url
    coll.remove({})
    get_xueqiu_hold(url)
    return url
"""
@app.route('/start', methods=['POST'])
def post_url():
    # get url
    projects.clear()
    ZHs0.clear()
    ZHs1.clear()    
    data = json.loads(request.data.decode())
    url = data["url"]
    #if 'https://' not in url[:8]:
    #    url = 'https://' + url
    #coll.remove({})
    url0 = 'https://xueqiu.com/stock/portfolio/stocks.json?size=1000&pid=-1&tuid='+url+'&cuid=1180102135&_=1477728185503'
    req = urllib.request.Request(url0,headers = {#'X-Requested-With': 'XMLHttpRequest',
           #'Referer': 'http://xueqiu.com/p/ZH010389',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
           #'Host': 'xueqiu.com',
           #'Connection':'keep-alive',
           #'Accept':'*/*',
           'cookie':cookie
           })
    html = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(html)
    for item in data["stocks"]:
        if re.search('ZH\d{6}',str(item)):
            ZHs0[item["code"]]=item["stockName"]
    for ZH0 in ZHs0:
        prof(ZH0)
    ZHs = re.findall('ZH\d{6}',data["portfolios"][0]["stocks"])
    for ZH in ZHs:
        get_xueqiu_hold("https://xueqiu.com/P/"+ZH)
    #get_xueqiu_hold(url)
    return url

@app.route("/data")
def data():
    """
    projects = coll.find({},{'stock_name':True,'weight':True,'_id':False})
    json_projects = []
    json_projects0 = {}
    for project in projects:
        #json_projects[project['stock_name']]=project['weight']
        json_projects.append(project)
    for json_project in json_projects:
        json_projects0[json_project['stock_name']]=json_project['weight']
    """
    projects0 = sorted(projects.items(), key=lambda x: (-x[1],x[0]))[:12]
    return jsonify(dict(projects0))

@app.route("/trans0")
def trans0():
    return jsonify(ZHs0)

@app.route("/trans1")
def trans1():
    return jsonify(ZHs1)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
