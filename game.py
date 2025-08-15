# -*- coding: utf-8 -*-

'''
用来在streamlit中搭建 语言类博弈环境
需要提供一个文件夹路径来
'''

from package import zhipu as zp
from package import dealJson as dj
from package import SparkApi as Sp
from package import getfromali as ga
import random 
import json
from typing import List
from package import Moonshot as ms
import time


class yuzhi():
    def __init__(self,data_path,data_api):
        self.data_path_question = data_path + "\\data_question.jsonl" # 储存问题
        self.data_path_state = data_path + "\\data_state.json" # 储存游戏环境的
        self.data_path = data_path
        self.data_path_chat = data_path + "\\data_chat.json"  # 储存chat记录
        self.api_path = data_api + "\data_api.json" #用来获取模型调用的api参数
        self.background = "“谁是卧底”是一款趣味策略游戏，通过描述和投票找出卧底词汇。游戏开始时，玩家随机获得一个词汇，其中一个词汇是卧底词汇。玩家轮流描述手中的词汇，但不能直接说出，同时要避免暴露身份。每轮描述后，所有玩家投票选出可能是卧底的人，得票最多的玩家被淘汰。游戏目标是找出卧底词汇，如果卧底撑到只剩下2个人，则卧底获胜；反之，如果卧底被提前淘汰，则大部队获胜。游戏过程中要注意描述时不要直接说出卡片上的词汇，同时尽量简略描述。你现在扮演一名游戏玩家。"

    def model_select(self,name:str ,user_input:str, model:str = "glm",temperature:float = 0.5):
        '''
        用来在 谁是卧底游戏中进行模型选择
        '''

        if model in ["generalv3","generalv3.5"]:
            _,answer_text,turn = Sp.getSpark(self.api_path ,user_input,self.data_path + f"\\data_{name}.json",temperature,model)
        if model in ["qwen-turbo","qwen-plus","qwen-max","chatglm-6b-v2","chatglm3-6b"]:
            temperature = temperature*2 - 0.01
            answer_text,turn = ga.alibaba_call_streaming(self.api_path,user_input,self.data_path + f"\\data_{name}.json",model,temperature)
        if model in ["glm-4","glm-3-turbo"]:
            answer_text,turn = zp.get_zhipu_text(self.api_path,user_input,self.data_path + f"\\data_{name}.json",model,temperature)
        if model in ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]:
            answer_text = ms.moonshot_chat_all(self.api_path,self.data_path + f"\\data_{name}.json",user_input,model,temperature)
            turn = 0
            time.sleep(1)
        return answer_text,turn



    def define_game(self,num): 
        '''
        用来确定游戏的基本信息
        '''
        with open(self.data_path_question,"r",  encoding='utf-8') as f: #读入题目信息
            num_c = 0 #随机选择题目
            chose_question = []
            for line in f:
                num_c += 1
                uint = json.loads(line)
                chose_question.append(uint[0])
            num_c -= 1
            random_number = random.randint(0, num_c)
            wodici = chose_question[random_number]["卧底词"]
            pingminci = chose_question[random_number]["平民词"]

        sequence = ["A", "B", "C", "D", "E", "F"]
        sequence = sequence[:num]

        wanjia = random.choice(sequence) # 为玩家分配身份
        random_element = random.choice(sequence) # 选择卧底玩家

        data = [
            {
                "num": 0,
                "player":wanjia,
                "wodi":random_element,
                "wodici":wodici,
                "pingminci": pingminci,
                "sequence": sequence,
                "state":"miaoshu-1",
            },
            "",
            "",
            ""
        ]

        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f, indent=4 ,ensure_ascii=False)

    def miaoshu_1(self): 
        '''
        用户输入之前的描述
        '''
        out = []
        with open(self.data_path_state,"r",  encoding='utf-8') as f:
            data = json.load(f)

        data[0]["num"] += 1
        num = data[0]["num"]
        data[1] += f"第{num}轮描述内容:\n"
        data[3] = "最近一轮描述内容:\n" #data[3]用来记录最近一次历史描述

        for name in data[0]["sequence"]:

            if not name == data[0]["player"]:

                if name == data[0]["wodi"]:
                    word = data[0]["wodici"]
                else:
                    word = data[0]["pingminci"]

                #大模型进行游戏环节
                dj.system_set(self.background + data[1] ,self.data_path + f"\\data_{name}.json")

                prompt = f"你扮演参赛者，你的词汇“{word}”，请你进行一次描述，只回答描述内容，不要进行解释，内容尽可能简短，要注意隐藏词汇的显著特征，可以描述词汇的外观、用途等一方面的特性。避免与其他玩家重复。" 

                answer,lunshu = self.model_select(name,prompt,"qwen-turbo",0.95)
                #answer,lunshu = zp.get_zhipu_text(self.api_path,prompt, self.data_path + f"\\data_{name}.json", "glm-4",0.95)
                try:
                    with open(self.data_path_chat,"r",  encoding='utf-8') as f:
                        chat_data = json.load(f)
                except FileNotFoundError:
                    chat_data = []
                out.append({
                    "role": f"{name}",
                    "content": answer
                })
                chat_data.append({
                    "role": f"{name}",
                    "content": answer
                })
                with open(self.data_path_chat,"w",  encoding='utf-8') as f:
                    json.dump(chat_data, f,indent=4, ensure_ascii=False)

                data[1] += f"玩家{name}:" + answer + "\n"
                data[3] += f"玩家{name}:" + answer + "\n"

            else:
                break

        data[0]["state"] = "miaoshu-2"
        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)
        return out    

    def miaoshu_2(self, text_input): 
        '''
        玩家描述之后
        '''
        out = []
        #写入玩家描述
        with open(self.data_path_chat,"r",  encoding='utf-8') as f:
            chat_data = json.load(f)
        chat_data.append({
                    "role": "user",
                    "content": text_input
                })
        out.append({
                    "role": "user",
                    "content": text_input
                })
        with open(self.data_path_chat,"w",  encoding='utf-8') as f:
            json.dump(chat_data, f,indent=4, ensure_ascii=False)

        #读取历史信息
        with open(self.data_path_state,"r",  encoding='utf-8') as f:
            data = json.load(f)
        index = data[0]["sequence"].index(data[0]["player"])
        data[1] += f"玩家{data[0]['player']}:" + text_input + "\n"
        data[3] += f"玩家{data[0]['player']}:" + text_input + "\n"
        
        # 如果玩家为最后一个描述则不麻烦
        if index == len(data[0]["sequence"])-1:
            pass

        else: 
            new_sequence = data[0]["sequence"][index+1:]

            for name in new_sequence:

                if name == data[0]["wodi"]:
                    word = data[0]["wodici"]
                else:
                    word = data[0]["pingminci"]

                #大模型进行游戏环节
                dj.system_set(self.background + data[1] ,self.data_path + f"\\data_{name}.json")

                prompt = f"你扮演参赛者，你的词汇“{word}”，请你进行一次描述，只回答描述内容，不要进行解释，内容尽可能简短，要注意隐藏词汇的显著特征，可以描述词汇的外观、用途等一方面的特性。避免与其他玩家重复。"

                answer,lunshu = self.model_select(name,prompt,"qwen-turbo",0.95)
                #answer,lunshu = zp.get_zhipu_text(self.api_path,prompt, self.data_path + f"\\data_{name}.json", "glm-4",0.95)
                    
                data[1] += f"{name}:" + answer + "\n"
                data[3] += f"玩家{name}:" + answer + "\n"

                with open(self.data_path_chat,"r",  encoding='utf-8') as f:
                    chat_data = json.load(f)
                chat_data.append({
                    "role": f"{name}",
                    "content": answer
                })
                out.append(
                    {
                    "role": f"{name}",
                    "content": answer
                })
                #记录历史数据
                with open(self.data_path_chat,"w",  encoding='utf-8') as f:
                    json.dump(chat_data, f,indent=4, ensure_ascii=False)
        
        #更新状态
        data[0]["state"] = "toupiao-1"
        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)
        return out


    def toupiao_1(self): #玩家之前投票

        '''
        玩家之前的投票
        '''
        out = []
        #读取历史信息
        with open(self.data_path_state,"r",  encoding='utf-8') as f:
            data = json.load(f)
        

        for name in data[0]["sequence"]:

            if not name == data[0]["player"]:

                if name == data[0]["wodi"]:
                    word = data[0]["wodici"]
                else:
                    word = data[0]["pingminci"]

                #大模型进行游戏环节
                dj.system_set(self.background + data[1] ,self.data_path + f"\\data_{name}.json")

                prompt = data[3] + f"你的词汇是“{word}”，请从描述玩家中选择与你的词汇不符的玩家，不要选择自己{name}，请一步一步思考，给出推理过程，包括判断自己是否为卧底。"

                answer,lunshu = self.model_select(name,prompt,"qwen-turbo",0.95)
                #answer,lunshu = zp.get_zhipu_text(self.api_path,prompt, self.data_path + f"\\data_{name}.json", "glm-4", 0.95)
                data[2] += f"{name}:" + answer + "\n"

                with open(self.data_path_chat,"r",  encoding='utf-8') as f:
                    chat_data = json.load(f)
                chat_data.append({
                    "role": f"{name}",
                    "content": answer
                })
                out.append(
                    {
                    "role": f"{name}",
                    "content": answer
                    }
                )

                #记录历史数据
                with open(self.data_path_chat,"w",  encoding='utf-8') as f:
                    json.dump(chat_data, f,indent=4, ensure_ascii=False)
            
            else:
                break
                
        data[0]["state"] = "toupiao-2"
        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)
        return out   

    def toupiao_2(self, text_input): 

        '''
        玩家之后投票
        '''
        out = []
        out_num = ""
         #读取历史信息
        with open(self.data_path_state,"r",  encoding='utf-8') as f:
            data = json.load(f)
        

        if data[0]["player"] != "NO":
            #写入玩家描述
            with open(self.data_path_chat,"r",  encoding='utf-8') as f:
                chat_data = json.load(f)
            chat_data.append({
                        "role": "user",
                        "content": text_input
                    })
            out.append(
                        {
                        "role": "user",
                        "content": text_input
                    }
            )
            with open(self.data_path_chat,"w",  encoding='utf-8') as f:
                json.dump(chat_data, f,indent=4, ensure_ascii=False)

            name = data[0]["player"]
            data[2] += f"{name}:" + text_input + "\n"
            index = data[0]["sequence"].index(data[0]["player"])
        else:
            index = len(data[0]["sequence"])-1
       
        
        # 如果玩家为最后一个描述则不麻烦
        if index == len(data[0]["sequence"])-1:
            print(data[2])

        else: 
            new_sequence = data[0]["sequence"][index+1:]
            for name in new_sequence:

                if name == data[0]["wodi"]:
                    word = data[0]["wodici"]
                else:
                    word = data[0]["pingminci"]

                #大模型进行游戏环节
                dj.system_set(self.background + data[1] ,self.data_path + f"\\data_{name}.json")

                prompt = data[3] + f"你的词汇是“{word}”，请从描述玩家中选择与你的词汇不符的玩家，不要选择自己{name}，请一步一步思考，请一步一步思考，给出推理过程，包括判断自己是否为卧底。"

                answer,lunshu = self.model_select(name,prompt,"qwen-turbo",0.95)
                # answer,lunshu = zp.get_zhipu_text(self.api_path,prompt, self.data_path + f"\\data_{name}.json", "glm-4", 0.95)
                data[2] += f"{name}:" + answer + "\n"

                with open(self.data_path_chat,"r",  encoding='utf-8') as f:
                    chat_data = json.load(f)
                chat_data.append({
                    "role": f"{name}",
                    "content": answer
                })

                out.append(
                    {
                    "role": f"{name}",
                    "content": answer
                }
                )

                #记录历史数据
                with open(self.data_path_chat,"w",  encoding='utf-8') as f:
                    json.dump(chat_data, f,indent=4, ensure_ascii=False)

        data[1] += f"第{data[0]['num']}轮投票环节\n" 
        data[1] += data[2]

        #对的票进行统计
        piao_record = []
        for item in data[0]["sequence"]:
            piao_record.append(data[2].count(item))

        # 找到列表中的最大值和其索引
        max_value = max(piao_record)
        # 找到所有最大值的索引
        max_index = [i for i, v in enumerate(piao_record) if v == max_value]

        if len(max_index) == 1:
            # 删除最大值所在的元素
            deleted_element = data[0]["sequence"].pop(max_index[0])

            out_num = deleted_element

            if deleted_element == data[0]["wodi"]:
                data[0]["state"] = "pingminwin"
                data[2] = out_num
                
            else:
                if len(data[0]["sequence"]) == 2:
                    data[0]["state"] = "wodiwin"
                    data[2] = out_num
                else:
                    data[0]["state"] = "miaoshu-1"
                    num = data[0]["num"]
                    
                    data[1] += f"第{num}轮投票，出局的玩家为{deleted_element}，Ta不是卧底\n"
                    data[2] = out_num

            if deleted_element == data[0]["player"]:
                data[0]["player"] = "NO"
        else:
            out_num = "无"
            num = data[0]["num"]
            data[0]["state"] = "miaoshu-1"
            data[1] += f"第{num}轮投票，没有出局的玩家\n"
            data[2] = out_num

        #记录数据
        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)


        with open(self.data_path_state,"w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)
        
        return out

    def read_state(self) -> List:
        '''
        用来阅读游戏的状态
        '''
        with open(self.data_path_state, "r",  encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def read_chat_record(self) -> List:
        '''
        用来阅读，游戏chat
        '''
        with open(self.data_path_chat, "r",  encoding='utf-8') as f:
            data = json.load(f)
        return data

    def write_chat_record(self, key:str,text: str ):
        '''
        key是游戏身份
        text是写入文字
        '''
        with open(self.data_path_chat, "r",  encoding='utf-8') as f:
            data = json.load(f)
        data.append({
            "role": key,
            "content": text
        })
        with open(self.data_path_chat, "w",  encoding='utf-8') as f:
            json.dump(data, f,indent=4, ensure_ascii=False)

    def delet_chat_record(self):
        '''
        用来清除play的历史记录开始新的回合
        '''
        with open(self.data_path_chat, "w",  encoding='utf-8') as f:
            json.dump([], f,indent=4, ensure_ascii=False)

    def modify_state(self,new_state: List) -> List:
        '''
        用来修改游戏的状态文件
        new_state为需要传入的游戏状态数据
        '''
        with open(self.data_path_state, "w",  encoding='utf-8') as f:
            json.dump(new_state, f,indent=4, ensure_ascii=False)









