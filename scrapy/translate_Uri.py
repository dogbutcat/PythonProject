# coding=utf-8
import json
import re
from math import floor
try:
    from urllib import request as urllib2
except ImportError:
    import urllib2
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import http.cookiejar

# response = urllib2.urlopen('http://placekitten.com/')
# cat_img = response.read()
# print(cat_img)

# 百度翻译url
baseUrl = 'https://fanyi.baidu.com/'
langDetectApi = 'langdetect'
transApi = 'v2transapi'
cj = http.cookiejar.CookieJar()
cookieProcessor = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookieProcessor)
cookie = 'locale=zh; BAIDUID=2C38C19D161A26C252CECF1F59CCFBF4:FG=1; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1517904022; from_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1517905073'

# data = {}
# data['from'] = 'en'
# data['to'] = 'zh'
# data['query'] = 'translate me'
# data['transtype'] = 'translang'
# data['simple_means_flag'] = 3
# data['sign'] = '200239.519454'  # generate from query phrase
# data['token'] = '3b95791d32f592e79420f42e6cb3f668' # from window.common.token

# req = urllib2.Request(url, urlencode(data).encode('utf-8'), headers, method='POST')

# response = urllib2.urlopen(req)

# responseHTML = response.read().decode('utf-8')
# responseJSON = json.JSONDecoder().decode(responseHTML)
# print(responseJSON);
# transResult = responseJSON['trans_result']
# print((transResult['data'][0]['dst']))
# print(transResult['phonetic'][0]['trg_str'])

# for i in transResult['phonetic']:
#     print(i['trg_str'])

def main_req(targetUrl,data=None,method='GET'):
    headers = {
        'Referer': 'https://fanyi.baidu.com/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        # 'Cookie': 'BAIDUID=C360EBAB8A03CA84A0E60771C649CDB1:FG=1; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; from_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1517812282; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1517812283'
        'Cookie': cookie
    }
    if(not isinstance(data, bytes) and (data is not None)):
        data = urlencode(data).encode('utf-8')
    req = urllib2.Request(targetUrl,data,headers,method=method);
    return opener.open(req);

def calculateSign(transStr, gtk):
    gtk_str = gtk
    strLen = len(transStr)
    if (strLen > 30):
        internalLen = floor(strLen / 2) - 5
        transStr = transStr[0:10] + transStr[internalLen:internalLen + 10] + transStr[-10:]
    # reg_pattern = re.compile('[\uD800-\uDBFF][\uDC00-\uDFFF]',re.I)
    # contain_utf16 = reg_pattern.match(transStr);
    # if(contain_utf16 == None):
    #     strLen = len(transStr)
    #     if(strLen>30):
    #         internalLen = floor(strLen/2)-5
    #         transStr = transStr[0:10]+transStr[internalLen:internalLen+10]+transStr[-10:]
    # else:
    #     # if contain_utf16 character, calculate length of input string whether over 30
    #     indexArr = reg_pattern.split(transStr)
    #     tempArr =[]
    #     for index in range(len(indexArr)):
    #         if(indexArr[index]!=''):
    #             tempArr.append(*list(indexArr[indexArr[index]]))
    #         if(index != len(indexArr)-1):
    #             tempArr.append(contain_utf16[index])
    #     tempLen = len(tempArr)
    #     if(tempLen>30):
    #         transStr = ''.join(tempArr[0,10])+''.join(tempArr[floor(tempLen/2)-5,floor(tempLen/2)+5])+''.join(tempArr[-10:])

    # deal each charactor
    high_split,low_split = gtk.split('.')
    # convert to number
    high_split = int(high_split)
    low_split = int(low_split)
    innerArr =[]
    i=0
    while i<len(transStr):
        temp_char_ascii = ord(transStr[i])
        if(temp_char_ascii<128):
            innerArr.append(temp_char_ascii)
        else:
            if(temp_char_ascii <2048):
                innerArr.append((temp_char_ascii >> 6) | 192)
            else:
                if (55296 == (64512 & temp_char_ascii) and i + 1 < transStr.length and 56320 == (64512 & ord(transStr[temp_index + 1]))):
                    i += 1
                    temp_char_ascii = 65536 + ((1023& temp_char_ascii)<<10)+(1023 & ord(transStr[i]))
                    innerArr.append(temp_char_ascii>>18|240)
                    innerArr.append(temp_char_ascii>>12|128)
                else:
                    innerArr.append(temp_char_ascii>>12|224)
                    innerArr.append((temp_char_ascii >> 6) & 63 | 128)

            innerArr.append(temp_char_ascii & 63 | 128)
        i += 1

    # deal list with certain order
    str_1 = chr(43) + chr(45) + chr(97) + (chr(94) + chr(43) + chr(54))
    str_2 = chr(43) + chr(45) + chr(51) + (chr(94) + chr(43) + chr(98)) + (chr(43) + chr(45) + chr(102))

    new_sum = high_split
    for index in range(len(innerArr)):
        new_sum+=innerArr[index]
        new_sum = reSum(new_sum,str_1)
    new_sum = reSum(new_sum, str_2)
    new_sum ^= low_split
    if(new_sum<0):
        new_sum = (2**31-1)&new_sum+2**31
    new_sum %= 1e6
    new_sum = int(new_sum)
    final_sum = str(new_sum)+'.'+str(new_sum^high_split)
    return final_sum


def reSum(targetNum,str2):
    for index in range(0, len(str2),3):
        third_char = str2[index+2]
        if(third_char>='a'):
            third_char = ord(third_char)-87
        else:
            third_char = int(third_char)
        if(str2[index+1] == '+'):
            third_char = (-1 &targetNum) >> third_char
        else:
            third_char = targetNum << third_char
        if(str2[index]== '+'):
            targetNum = (targetNum+third_char)& (2**32-1)
        else:
            targetNum = targetNum ^ third_char
    return targetNum

if __name__ == '__main__':
    query_string = input('Please input your TEXT to translate: ')
    data = {
        'query': query_string,
    }
    response = main_req(baseUrl+langDetectApi,data,method='POST')
    responseTypeJSON = json.JSONDecoder().decode(response.read().decode('utf-8'))
    response = main_req(baseUrl)
    responseHTML = response.read().decode('utf-8')
    gtk = re.findall(r'window\.gtk\s=\s[\'\"](.*)[\'\"];',responseHTML)[0];
    token = re.findall(r'token:\s[\'\"](.*)[\'\"],',responseHTML)[0];
    gen_sign = calculateSign(query_string,gtk)
    targetLan = 'zh'
    if(targetLan == responseTypeJSON['lan']):
        targetLan = 'en'
    data = {
        'from':responseTypeJSON['lan'],
        'to': targetLan,
        'query': query_string,
        'transtype':'translang',
        'simple_means_flag':3,
        'sign': gen_sign,
        'token': token
    }
    response = main_req(baseUrl+transApi, data,'POST')
    responseJSON = json.JSONDecoder().decode(response.read().decode('utf-8'))
    transResult = responseJSON['trans_result']
    print((transResult['data'][0]['dst']))

    if('phonetic' in transResult):
        for i in transResult['phonetic']:
            print(i['trg_str'])
