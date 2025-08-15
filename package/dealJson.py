import json
import os

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
    with open(file_path_json, 'w', encoding='utf-8') as file:
            json.dump(system_content, file, indent=4, ensure_ascii=False)

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

def read_history_json(file_path:str) -> list:
    '''
    用来读取历史信息
    file_path 用来传入数据的地址
    '''
    try:
        with open(file_path, 'r',encoding='utf-8' ) as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []
    return existing_data

def write(file_path_json: str,text: str,user: str ):
    '''
    记录历史信息
    file_path_json为文件储存位置
    text 为写入内容
    user 为角色
    '''
    data =  read_history_json(file_path_json)
    data.append({"role": user, "content": text})
    with open(file_path_json, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)