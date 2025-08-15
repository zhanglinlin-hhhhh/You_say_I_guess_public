# -*- coding:utf-8 -*-
# author: Ysh
#这个库根据讯飞星火的webdemo进行改编
#通过api 进行语音的合成
#本demo测试时运行的环境为：Windows + Python3.9
#错误码链接：https://www.xfyun.cn/document/error-code 
#相关参考：https://www.xfyun.cn/doc/tts/online_tts/API.html

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
from typing import Literal

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


def vocie(path_api,text_from_user:str, vcn_f: Literal['xiaoyan', 'aisjiuxu', 'aisxping', 'aisjinger', 'aisbabyxu'], speed_f: float, volume_f: float, pitch_f: float, file_path: str) -> None:
    '''
    用语调用讯飞星火模型获取音频

    输入变量

    text_from_user 要生成的文本内容
    vcn_f 选择的角色
    speed_f 速度
    volume_f 音量
    pitch_f 音高
    file_path 文件路径

    需要填入api相关的参数

    '''


    global file_voice 
    file_voice = file_path
    
    STATUS_FIRST_FRAME = 0  # 第一帧的标识
    STATUS_CONTINUE_FRAME = 1  # 中间帧标识
    STATUS_LAST_FRAME = 2  # 最后一帧的标识


    class Ws_Param(object):
        # 初始化
        #vcn为发音人
        def __init__(self, APPID, APIKey, APISecret, Text, speed, vcn, volume, pitch):
            self.APPID = APPID
            self.APIKey = APIKey
            self.APISecret = APISecret
            self.Text = Text

            # 公共参数(common)
            self.CommonArgs = {"app_id": self.APPID}
            # 业务参数(business)，更多个性化参数可在官网查看
            self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": vcn,"tte": "utf8", 'speed': speed ,'volume': volume,'pitch':pitch}
            self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
            #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
            #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

        # 生成url
        def create_url(self):
            url = 'wss://tts-api.xfyun.cn/v2/tts'
            
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))

            # 拼接字符串
            signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                    digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": "ws-api.xfyun.cn"
            }
            # 拼接鉴权参数，生成url
            url = url + '?' + urlencode(v)
            # print("date: ",date)
            # print("v: ",v)
            # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
            # print('websocket url :', url)
            return url

    def on_message(ws, message):
        try:
            message =json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open(file_voice, 'ab') as f:
                    f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)



    # 收到websocket错误的处理
    def on_error(ws, error):
        print("### error:", error)


    # 收到websocket关闭的处理
    def on_close(ws):
        print("### closed ###")


    # 收到websocket连接建立的处理
    def on_open(ws):
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                "business": wsParam.BusinessArgs,
                "data": wsParam.Data,
                }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
        thread.start_new_thread(run, ())

    
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 如果文件存在，删除它
        os.remove(file_path)

    appid,api_secret,api_key = get_api(path_api)

    # 测试时候在此处正确填写相关信息即可运行
    wsParam = Ws_Param(APPID=appid, APISecret=api_secret,
                    APIKey=api_key,
                    Text= text_from_user,
                    speed=speed_f, 
                    vcn=vcn_f, 
                    volume=volume_f, 
                    pitch=pitch_f)

    websocket.enableTrace(False) #禁用WebSocket的调试信息输出
    wsUrl = wsParam.create_url() 
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
