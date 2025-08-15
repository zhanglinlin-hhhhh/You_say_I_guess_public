from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests
from typing import Tuple

def get_api(data_path:str)-> str:
    '''
    用来获取模型调用所需要的API参数
    返回参数 appid,api_secret,api_key
    '''
    with open(data_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
        appid = data[0]["SparkApi"]["appid"]
        api_secret = data[0]["SparkApi"]["api_secret"]
        api_key = data[0]["SparkApi"]["api_key"]
    return appid,api_secret,api_key


def get_text_form_picture(path_api,file_data) -> Tuple[str,str]:

    '''
    这个函数是用来从图片获得文字
    图像数据base64编码后大小不得超过10M
    其中 APPId APISecret APIKey 需要从讯飞开放平台控制台获取
    支持中英文,支持手写和印刷文字。
    
    输入变量：
    file_data 图片的数据

    输出变量：
    result:文本一行形式输出
    result_n: 分段输出，添加了\n
    '''

    appid,api_secret,api_key = get_api(path_api)

    APPId = appid  # 控制台获取
    APISecret = api_secret  # 控制台获取
    APIKey = api_key  # 控制台获取

    # with open(file_path, "rb") as f:
    #     imageBytes = f.read()
    imageBytes = file_data

    class AssembleHeaderException(Exception):
        def __init__(self, msg):
            self.message = msg


    class Url:
        def __init__(self, host, path, schema):
            self.host = host
            self.path = path
            self.schema = schema
            pass


    # calculate sha256 and encode to base64
    def sha256base64(data):
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest


    def parse_url(requset_url):
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + requset_url)
        path = host[edidx:]
        host = host[:edidx]
        u = Url(host, path, schema)
        return u


    # build websocket auth request url
    def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
        u = parse_url(requset_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        print(date)
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        print(signature_origin)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        print(authorization_origin)
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }

        return requset_url + "?" + urlencode(values)


    url = 'https://api.xf-yun.com/v1/private/sf8e6aca1'

    body = {
        "header": {
            "app_id": APPId,
            "status": 3
        },
        "parameter": {
            "sf8e6aca1": {
                "category": "ch_en_public_cloud",
                "result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json"
                }
            }
        },
        "payload": {
            "sf8e6aca1_data_1": {
                "encoding": "jpg",
                "image": str(base64.b64encode(imageBytes), 'UTF-8'),
                "status": 3
            }
        }
    }

    request_url = assemble_ws_auth_url(url, "POST", APIKey, APISecret)

    headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': APPId}
    print(request_url)
    response = requests.post(request_url, data=json.dumps(body), headers=headers)
    print(response)
    print(response.content)

    print("resp=>" + response.content.decode())
    tempResult = json.loads(response.content.decode())

    finalResult = base64.b64decode(tempResult['payload']['result']['text']).decode()
    finalResult = finalResult.replace(" ", "").replace("\n", "").replace("\t", "").strip()
    finalResult = json.loads(finalResult)
    result = ""
    result_n = ""
    for item in finalResult["pages"][0]["lines"]:
        item_text = item["words"][0]["content"]
        result += item_text
        result_n += item_text 
        result_n += "\n"
        print(item_text)

    return result, result_n