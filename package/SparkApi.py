# -*- coding:utf-8 -*-
# author: Ysh
#这个库根据讯飞星火的webdemo进行改编
#用来实现模型api的使用
#建立了 Json 数据库来储存背景与历史记录


import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client
import os
from typing import Tuple, Optional

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

def getSpark(path_api: str, question_frommain: str,file_path_json: str,temperature: float = 0.5,domain: str ="generalv3") -> Tuple[list[str],str,int]:

    '''
    用于从讯飞平台获取大模型服务

    输入变量：
    question_frommain 用来传入输入的文字内容
    file_path用来传入Json数据的保存地址
    temperature 用来调节模型的灵活性
    domain为版本号 默认使用星火 3.0版本
    使用3模型时无法使用system功能 "generalv3" "generalv3.5"

    返回变量：
    answer 生成内容的列表
    answer_text 生成内容的文本
    lunshu 基于多少轮数对话进行内容生成

    备注
    需要填入
    APPID, APIKey, APISecret 等参数
    '''


    global temperature_copy
    temperature_copy = temperature

    global answer
    answer = []

    class Ws_Param(object):
        # 初始化
        def __init__(self, APPID, APIKey, APISecret, Spark_url):
            self.APPID = APPID
            self.APIKey = APIKey
            self.APISecret = APISecret
            self.host = urlparse(Spark_url).netloc
            self.path = urlparse(Spark_url).path
            self.Spark_url = Spark_url

        # 生成url
        def create_url(self):
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))

            # 拼接字符串
            signature_origin = "host: " + self.host + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + self.path + " HTTP/1.1"

            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                    digestmod=hashlib.sha256).digest()

            signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

            authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": self.host
            }
            # 拼接鉴权参数，生成url
            url = self.Spark_url + '?' + urlencode(v)
            # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
            return url


    # 收到websocket错误的处理
    def on_error(ws, error):
        print("### error:", error)


    # 收到websocket关闭的处理
    def on_close(ws,one,two):
        print(" ")


    # 收到websocket连接建立的处理
    def on_open(ws):
        thread.start_new_thread(run, (ws,))


    def run(ws, *args):
        data = json.dumps(gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
        ws.send(data)


    # 收到websocket消息的处理
    def on_message(ws, message):
        # print(message)
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            print(content,end ="")
            answer.append(content)
            if status == 2:
                ws.close()


    def gen_params(appid, domain,question):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": temperature_copy,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data


    def main(appid, api_key, api_secret, Spark_url,domain, question):
        # print("星火:")
        wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
        ws.appid = appid
        ws.question = question
        ws.domain = domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    appid,api_secret,api_key = get_api(path_api)

    # #以下密钥信息从控制台获取
    # appid = "f006a074"     #填写控制台中获取的 APPID 信息
    # api_secret = "MWFmNGIyMWJiMDQ2MzgzN2FhMGY2NzNk"   #填写控制台中获取的 APISecret 信息
    # api_key ="156d41c0ca3f85710e4e000036c89f0f"    #填写控制台中获取的 APIKey 信息

    #用于配置大模型版本，默认“general/generalv2”
    #domain = "generalv3.0"
    #domain = "general"   # v1.5版本nih
    # domain = "generalv2"    # v2.0版本
    #云端环境的服务地址
    #Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
    #Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址

    if domain == "generalv3":
        Spark_url = "wss://spark-api.xf-yun.com/v3.1/chat" # v3.0环境的地址
    elif domain == "generalv3.5":
        Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat" # v3.0环境的地址

    def getText2(role,content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        return jsoncon
    

    def read_json_file(file_path):
        # 读取原有的JSON文件内容
        try:
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []
        return existing_data


    
    #用来记录对话的信息
    def Json_write_his(file_path, user, ai):

        # 准备要写入的数据
        new_data_user = {
            "role": "user",
            "content": user,
        }

        new_data_ai = {
            "role": "assistant",
            "content": ai,
            
        }

        # 读取原有的JSON文件内容
        existing_data = read_json_file(file_path)

        # 添加新的数据
        existing_data.append(new_data_user)
        existing_data.append(new_data_ai)

        # 将更新后的数据写入JSON文件
        with open(file_path, 'w') as file:
            json.dump(existing_data, file, indent=4)
        
    #返回目前的对话轮数
    def json_content_length(existing_data, question):

        re_num = 0 #这个变量用于记录采用历史对话的轮数

        if existing_data == []:
            
            existing_data.insert(0,question)
            return existing_data, re_num
    
        length_text = 10000
        text_all = ""
        flag = 0
        #对信息长度进行检查
        existing_data.append(question)
        
        while (length_text > 4000):


            for item in existing_data:
                if item["role"] == "system":
                    flag = 1
                    text_all += item["content"]
                else:
                    pass
                text_all += item["content"]
            length_text = len(text_all)

            if flag == 1:
                if length_text > 8000:
                    del existing_data[1:3]
                else:
                    re_num = (len(existing_data) - 2)/2
            else:
                if length_text > 8000:
                    del existing_data[:2]
                else:
                    re_num = (len(existing_data) - 1)/2

        return existing_data, re_num


    data_his = read_json_file(file_path_json)
    
    question, lunshu = json_content_length(data_his, getText2("user",question_frommain))

    print("星火:",end = "")
    main(appid,api_key,api_secret,Spark_url,domain,question)

    answer_text = "".join(answer)

    Json_write_his(file_path_json,question_frommain,answer_text)
    return answer, answer_text, int(lunshu)



def new_converation(file_path_json: str) -> None:
    '''
    建立新的对话，将历史数据删除

    file_path_json 是目标函数位置
    '''
    
    if os.path.exists(file_path_json):
        os.remove(file_path_json)


def system_set(text: str,file_path_json: str) -> None:
    '''
    写入聊天背景

    text:要写入的内容
    file_path_json:目标文件的路径
    '''
    new_converation(file_path_json)
    system_content = [{"role": "system", "content": text}]
    with open(file_path_json, 'w') as file:
            json.dump(system_content, file, indent=4)

def find_system(file_path_json: str) -> str:
    '''
    查找当前的记录中有没有system
    如果有的话，返回system的内容

    file_path_json:目标文件的路径
    '''

    text = ""
    try:
         with open(file_path_json, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
            existing_data = []
    
    for data in existing_data:
        if data["role"] == "system":
            text += data["content"]

    return text

