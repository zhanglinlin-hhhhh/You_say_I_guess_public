#使用阿里提供的云平台，api调用相关模型
# YSH 24.03.01
# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html

import dashscope
import json
import os
from typing import Tuple,Literal

#可调用的模型，有一定时间期限与免费额度
# qwen-turbo
# qwen-plus
# qwen-max 限时免费
# baichuan2-13b-chat-v1
# chatglm-6b-v2
# chatglm3-6b 限时免费

def get_api(data_path:str)-> str:
    '''
    用来获取模型调用所需要的API参数
    '''
    with open(data_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    return data[0]["alibabaApi"]["api_key"]

def getText2(role,content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        return jsoncon
    

def read_json_file(file_path):
    # 读取原有的JSON文件内容
    try:
        with open(file_path, 'r',encoding='utf-8') as file:
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
    
    while (length_text > 3000):


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



def alibaba_call_streaming( data_api:str , prompt_text: str, json_path_Qwen:str ,model_input:str = Literal['qwen-turbo','qwen-plus','qwen-max','baichuan2-13b-chat-v1','chatglm-6b-v2','chatglm3-6b'], temperature:float = 0.85)->Tuple[str,int]:
    '''
    用于从阿里云获取模型服务

    输入变量：
    promp_text 输入模型的内容
    json_path_Qwen 存储对话内容的文件lujing
    model_input 选择的模型参数 阿里提供了不少可以调用的模型
    temperature 控制模型生成的随机性

    备注：
    需要在该函数中填入必要的API相关参数
    '''

    
    dashscope.api_key = get_api(data_api)
    data_his = read_json_file(json_path_Qwen)
    
    question, lunshu = json_content_length(data_his, getText2("user",prompt_text))
   
    response_generator = dashscope.Generation.call(
        model=model_input,
        messages= question,
        temperature = temperature,
        top_p=0.8)

    paragraph = response_generator.output['text']

    print(paragraph)

    Json_write_his(json_path_Qwen, prompt_text, paragraph)
    
    return paragraph,int(lunshu)

#建立新的对话，将历史数据删除
def new_converation(file_path_json):
    if os.path.exists(file_path_json):
        os.remove(file_path_json)

#写入聊天背景
def system_set(text,file_path_json):
    new_converation(file_path_json)
    system_content = [{"role": "system", "content": text}]
    with open(file_path_json, 'w') as file:
            json.dump(system_content, file, indent=4)

def find_system(file_path_json):

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