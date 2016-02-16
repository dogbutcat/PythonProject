# coding=utf-8
import json
import urllib2
import urllib

response = urllib2.urlopen('http://placekitten.com/')
cat_img = response.read()
# print(cat_img)

# 百度翻译url
url = 'http://fanyi.baidu.com/v2transapi'

data = {}
data['from']='en'
data['to']='zh'
data['query']='translate it from web'
data['transtype']='trans'
data['simple_means_flag']=3


response = urllib2.urlopen(url,urllib.urlencode(data))
responseHTML = response.read().decode('utf-8')
responseJSON = json.JSONDecoder().decode(responseHTML)
transResult = responseJSON['trans_result']
print((transResult['data'][0]['dst']))
print(transResult['phonetic'][0]['trg_str'])

# for i in transResult['phonetic']:
#     print(i['trg_str'])