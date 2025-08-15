
from zhipuai import ZhipuAI
import json
import os
from typing import Tuple,Literal

#glm-3-turbo
#glm-4

def get_api(data_path:str)-> str:
    '''
    用来获取模型调用所需要的API参数
    '''
    with open(data_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    return data[0]["zhipuApi"]["api_key"]

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
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
    
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
                text_all += str(item["content"])
            else:
                pass
            text_all += str(item["content"])
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

#temperature (0,1) 不取两端

def get_zhipu_text(path_api:str, text_input:str, data_path:str, model:str = Literal["glm-4","glm-3-turbo"], temperature = 0.95 )->Tuple[str,int]:
    '''
    用于从智谱ai服务端获取模型的响应

    输入参数：
    text_input 输入的内容
    data_path 文件路径
    model 选择的模型
    temperature 控制模型生成内容的随机性 范围是(0,1) 不能取两个端值

    备注：
    在函数中，需要填入api相关信息
    '''
    api_key = get_api(path_api)
    data_his = read_json_file(data_path)
    question, lunshu = json_content_length(data_his, getText2("user",text_input))#这两个函数和一下 留意

    client = ZhipuAI(api_key = api_key) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages= question,
        temperature=temperature,
    )
    print(response.choices[0].message.content)

    Json_write_his(data_path, text_input, response.choices[0].message.content)
    return response.choices[0].message.content,lunshu


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

def zhipu_send_get_only(path_api:str, data_path:str, model:str = Literal["glm-4.5-flash"], temperature = 0.95 ) -> str:
    '''
    不输入prompt 与处理
    读取历史记录后直接进行发送
    '''
    api_key = get_api(path_api)
    data_his = read_json_file(data_path)
    client = ZhipuAI(api_key = api_key) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages= data_his,
        temperature=temperature,
    )
    print(response.choices[0].message.content)
    data_his.append({"role": "assistant", "content":response.choices[0].message.content})
    
    # 将更新后的数据写入JSON文件
    with open(data_path, 'w', encoding='utf-8') as file:
        json.dump(data_his, file, indent=4, ensure_ascii=False)

    return response.choices[0].message.content
