from openai import OpenAI
from typing import List, Dict, Literal
import json

def get_api(data_path:str)-> str:
    '''
    用来获取模型调用所需要的API参数
    '''
    with open(data_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    return data[0]["MoonshotApi"]["api_key"]


def read_his(data_path:str) -> List :
    '''
    用来读取，历史信息
    '''
    try:
        with open(data_path, 'r',encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []

def new_turn(data_path:str):
    '''
    删除历史记录
    '''
    with open(data_path, 'w',encoding='utf-8') as file:
        json.dump([], file)

def system_set(data_path:str,text:str):
    '''
    在向ai发送的内容，添加system内容
    '''
    data = [{
        "role": "system", "content": text
    }]

    with open(data_path, 'w',encoding='utf-8') as file:
        json.dump(data, file,ensure_ascii=False,indent=4)

def prompt_record(data_path:str,text:str) -> List:
    '''
    在history_record中添加 prompt信息
    '''
    data = read_his(data_path)
    prompt = {"role": "user", "content": text}
    data.append(prompt)
    with open(data_path, 'w',encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return data
    
def response_record(data_path:str,text:str):
    '''
    在history_中记录response信息
    '''
    data = read_his(data_path)
    response = {"role": "assistant", "content": text}
    data.append(response)
    with open(data_path, 'w',encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def moonshot_chat_single(data_api:str,data_list:List, model: str=Literal["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k"],temperature = 0.3) -> str:
    '''
    简单调用Moonshot的api
    不进行历史记录
    目前是 moonshot-v1-8k,moonshot-v1-32k,moonshot-v1-128k 其一
    '''
    
    client = OpenAI(
    api_key=get_api(data_api),
    base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
    model = model,
    messages = data_list,
    temperature = temperature,
    )

    return completion.choices[0].message.content

def moonshot_chat_all(data_api:str,data_path:str, prompt:str, model: str=Literal["moonshot-v1-8k","moonshot-v1-32k","moonshot-v1-128k"],temperature = 0.3):
    '''
    完整的调用api,包括记录历史
    返回模型的回答
    '''
    data_input = prompt_record(data_path,prompt)
    response = moonshot_chat_single(data_api,data_input, model,temperature)
    response_record(data_path,response)
    return response


# client = OpenAI(
#     api_key="sk-dTNOn0mOEjyRSTPHDZUKStKKrKgkHc8YGf9tTn6jXmuE2O5j",
#     base_url="https://api.moonshot.cn/v1",
# )

# completion = client.chat.completions.create(
#   model="moonshot-v1-8k",
#   messages=[ 
#     {"role": "user", "content": "你好，我叫李雷，1+1等于多少？"}
#   ],
#   temperature=0.3,
# )

# print(completion.choices[0].message)

# print(moonshot_chat_all(r"F:\plat\data\data_api.json",r"F:\plat\data\data_his.json","你好，我叫李雷，1+1等于多少？","moonshot-v1-8k",0.3))