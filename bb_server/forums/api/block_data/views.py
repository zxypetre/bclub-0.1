from flask import jsonify
from flask.views import MethodView
from forums.func import get_json, object_as_dict
from .models import B_Picture
from forums.extension import redis_data
import requests
import math
import json

class Currency_News(MethodView):
    def get(self, token):
        headers = {'Content-Type':'application/json'}
        details = requests.get('https://block.cc/api/v1/coin/get?coin=%s'%(token), headers = headers)
        #kline = requests.get('https://block.cc/api/v1/marketKline/%s'%(token), headers = headers)
        total_market_cap_usd = requests.get('https://block.cc/api/v1/getBaseTotalInfo')
        total_market_cap_usd = total_market_cap_usd.json()['data']["total_market_cap_usd"]
        details = details.json()['data']
        keys = ['id','name', 'symbol','price', 'volume_ex', "supple", "available_supply", 'marketCap', 'level',
         'change1h', 'change7d', 'zhName', 'volume_level', 'low1d', 'high1d', 'CNY_RATE', 'BTC_RATE', 'ETH_RATE']
        data = {}
        for i in keys:
            data[i] = details[i]
        data['global_market_rate'] = ('%.2f%%' % (data['marketCap']/total_market_cap_usd * 100))
        data['Circulation_rate'] = ('%.2f%%' % (data['available_supply']/data['supple'] * 100))
        data['picture'] = 'https://blockchains.oss-cn-shanghai.aliyuncs.com/static/coinInfo/%s.png'%(token)
        '''try:
            kline.json()['data']['name']
        except: 
            return get_json(0, '数据错误，请重新请求', data)
        else:
            data['kline'] = kline.json()['data']'''
        return get_json(1, 'success', data)

class K_Line(MethodView):
    def get(self, token):
        if redis_data.exists(token):
            data = json.loads(redis_data.get(token))
            return get_json(1, 'success', data)
        headers = {'Content-Type':'application/json'}
        kline = requests.get('https://block.cc/api/v1/marketKline/%s'%(token), headers = headers)
        try:
            kline.json()['data']['name']
            data = kline.json()['data']
            redis_data.set(token, json.dumps(data), ex=3600) 
            return get_json(1, 'success', data)
        except:
            return get_json(0, '数据错误，请重新请求', {})

class B_List(MethodView):
    def get(self, page, limit):
        offset = (int(page)-1)*int(limit)
        blist = requests.get('https://api.tokenclub.com/v2/ticker/summary?type=0&offset=%s&limit=%s'%(offset, limit))
        blist = blist.json()['data']
        blist['page_count'] = int(math.ceil(int(blist['count'])/int(limit)))
        for i in blist['summaryList']:
            i['picture'] = 'https://blockchains.oss-cn-shanghai.aliyuncs.com/static/coinInfo/%s.png'%(i['id'])
        return get_json(1, 'success', blist)

class Picture(MethodView):
    def get(self):
        pictures = B_Picture.query.order_by('id').all()
        blist = requests.get('https://api.tokenclub.com/v2/ticker/summary?type=0&offset=%s&limit=%s'%(0, 3))
        blist = blist.json()['data']['summaryList']
        picturelist = []
        data = []
        for i in pictures:
            picturelist.append(object_as_dict(i)['picture'])
        for j in blist:
            Blist = {}
            Blist['id'] = j['id']
            Blist['symbol'] = j['symbol']
            Blist['name_ch'] = j['name_ch']
            data.append(Blist)
        for p in range(3):
            data[p]['picture'] = picturelist[p]
        return get_json(1, '币讯图片', data)
