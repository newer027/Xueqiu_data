# -*- coding: utf-8 -*-

import json
import re
import urllib.request
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import time
import pandas

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
projects = {}
ZHs0={}
ZHs1={}
cookie = 's=7017rril9u; xq_a_token=c4a084fe79a31a6ead299d4d49d622cab3b3b65e; xqat=c4a084fe79a31a6ead299d4d49d622cab3b3b65e; xq_r_token=fc287dc024ce197b1a0e1def6f674c260357bebf; xq_is_login=1; u=1180102135; xq_token_expire=Tue%20Mar%2014%202017%2016%3A56%3A10%20GMT%2B0800%20(CST); bid=45efaa8643ba70c7f4357d0930ff99d4_iz9kzepe'

def prof(url_ap0):
    url = 'https://xueqiu.com/cubes/rebalancing/history.json?cube_symbol='+url_ap0+'&count=20&page=1'
    req = urllib.request.Request(url,headers = {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
           'cookie':cookie
           })
    html = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(html)

    for i in range (len(data['list'])):
        for j in range(len(data['list'][i]['rebalancing_histories'])):
            if pandas.isnull(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted']):
                data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] = str(0)
            else:
                data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] = str(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'])
            if pandas.isnull(data['list'][i]['rebalancing_histories'][j]['target_weight']):
                data['list'][i]['rebalancing_histories'][j]['target_weight'] = str(0)
            else:
                data['list'][i]['rebalancing_histories'][j]['target_weight'] = str(data['list'][i]['rebalancing_histories'][j]['target_weight'])
    try:
        for i in range(len(data['list'])):
            localtime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(data['list'][i]['updated_at'] / 1000))
            if (time.time() - (data['list'][i]['updated_at'] / 1000)) < 86400*20:
                for j in range(len(data['list'][i]['rebalancing_histories'])):
                    ZHs1[j-data['list'][i]['updated_at']]=(localtime,url_ap0,ZHs0[url_ap0],data['list'][i]['rebalancing_histories'][j]['stock_name'] + ': '+ data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'] + '% ' + ("⬆" if float(data['list'][i]['rebalancing_histories'][j]['prev_weight_adjusted'])<float(data['list'][i]['rebalancing_histories'][j]['target_weight']) else "⇩") + ' '+ data['list'][i]['rebalancing_histories'][j]['target_weight'] + '%')
    except:
        print("exception occured")


def get_xueqiu_hold(url):
    req = urllib.request.Request(url,headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
                'cookie':cookie
               })
    soup = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(soup, 'lxml')
    script = soup.find('script', text=re.compile('SNB\.cubeInfo'))
    json_text = re.search(r'^\s*SNB\.cubeInfo\s*=\s*({.*?})\s*;\s*$',
                      script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    data = json.loads(json_text)
    for d in data["view_rebalancing"]["holdings"]:
        if d['stock_name'] in projects.keys():
            projects[d['stock_name']] += d['weight']            
        else:
            projects[d['stock_name']]= d['weight']
    

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/start', methods=['POST'])
def post_url():
    # get url
    projects.clear()
    ZHs0.clear()
    ZHs1.clear()    
    data = json.loads(request.data.decode())
    url = data["url"]
    url0 = 'https://xueqiu.com/stock/portfolio/stocks.json?size=1000&pid=-1&tuid='+url+'&cuid=1180102135&_=1477728185503'
    req = urllib.request.Request(url0,headers = {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
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
    return url

@app.route("/data")
def data():
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