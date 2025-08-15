import json
from typing import List
import os

class Flag:
    def __init__(self,data_path):
        self.data_path_rlhf = data_path
        self.data_rlhf_state = data_path + "\\data_record_state.json"

    def read_state(self) -> List:
        '''
        读取RLHF标注中的状态文件
        '''
        try:
            with open(self.data_rlhf_state,'r',encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = [
                        {
                        "list":[],
                        "now_file":"",
                        }
                    ]
            with open(self.data_rlhf_state,'w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=4)
        return data
    
    def write_state(self,data:List):
        '''
        用于更改 rlhf状态文件的 记录
        '''
        with open(self.data_rlhf_state,'w',encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False,indent=4)

    def check_valid(self,data_path:str):
        '''
        检查文件路径是否有效
        '''
        try:
            with open(data_path,'r',encoding='utf-8') as f:
                f.close()
                if data_path.endswith(".jsonl"):
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False
        
    def find_history(self,file_path:str)->dict:
        '''
        读取当前要处理的数据
        '''
        name = os.path.basename(file_path).replace(".","") + "RLHF_state.jsonl"
        with open(self.data_rlhf_state,'r',encoding='utf-8') as f:
            data = json.load(f)

        if name in data[0]:
            line = data[0][name]
        else:
            with open(file_path,'r',encoding='utf-8') as f2:
                for item in f2:
                    line = json.loads(item)
                    break

            data[0][name] = line
            with open(self.data_rlhf_state,'w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=4)
        return line
    
    def add_jsonl(self,data_path:str,data:dict):
        '''
        记录标记后的数据
        '''
        name = os.path.basename(data_path).replace(".","") + "RLHF.jsonl"

        with open(os.path.join(self.data_path_rlhf,name),"a",encoding='utf-8') as f:
            json.dump(data,f,ensure_ascii=False)
            f.write("\n")

    def next_one(self):
        '''
        更新处理的对象
        '''
        print(1)
        with open(self.data_rlhf_state,'r',encoding='utf-8') as f:
            data = json.load(f)
        name = os.path.basename(data[0]["now_file"]).replace(".","") + "RLHF_state.jsonl"
        last_one = data[0][name]
        
        flag = False
        with open(data[0]["now_file"],'r',encoding='utf-8') as f:
            for item in f:
                item = json.loads(item)
                if flag:
                    data[0][name] = item
                    break
                if item == last_one:
                    flag =True

        if last_one == data[0][name]:
            return False
        else:
            with open(self.data_rlhf_state,'w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=4)
            return True
        
    def clear(self,data_path:str) ->str :
        '''
        对重复数据进行清洗,存储到plat文件夹中
        '''

        name = os.path.basename(data_path).replace(".jsonl","") + "_cleared.jsonl"
        with open(data_path, 'r',encoding='utf-8') as file:
            lines = file.readlines()
            unique_data = []
            for line in lines:
                data = json.loads(line)
                if data not in unique_data:
                    unique_data.append(data)

        with open(os.path.join(self.data_path_rlhf, name), 'w',encoding='utf-8') as file:
            for data in unique_data:
                json.dump(data, file)
                file.write('\n')
        
        return os.path.join(self.data_path_rlhf, name)




