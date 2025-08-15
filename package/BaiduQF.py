import requests
import json
from typing import List,Tuple

def get_api_sys(path:str):
    '''
    用来获取api与相关参数

    返回的变量依次为：API_KEY,SECRET_KEY,url
    '''
    with open(path,'r',encoding='utf-8') as f:
        data = json.load(f)
        API_KEY = data[0]["BaiduQFApi"]["API_KEY"]
        SECRET_KEY = data[0]["BaiduQFApi"]["SECRET_KEY"]
        url = data[0]["BaiduQFApi"]["url"]
    return API_KEY,SECRET_KEY,url

def call_Baidu_api(API_KEY:str, SECRET_KEY:str, url:str, input_text:str, temperature:float = 0.5 )->str:

    '''
    这个函数为了调用百度千帆提供的api而编写
    API_KEY:千帆平台获取
    SECRET_KEY:千帆平台获取
    url: 千帆平台获取，不带?access_token=
    input_text:要发送的内容

    这个函数内部不提供,历史记录
    '''
    
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    access_token = str(requests.post("https://aip.baidubce.com/oauth/2.0/token", params=params).json().get("access_token"))
    
    #该部分为要发送的信息
    payload = json.dumps({
    "messages": [
        {
            "role": "user",
            "content": input_text
        }
        ],
    "temperature": temperature
    })

    url += "?access_token=" + access_token

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response = json.loads(response.text)

    return response["result"]


