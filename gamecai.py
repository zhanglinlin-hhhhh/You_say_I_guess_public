import json
import random
from package import dealJson as dj
from typing import List,Tuple, Literal


class gamenishuowocai():
    def __init__(self,data_game):
        self.record_state = data_game + "\\data_state.json"
        self.game_question = data_game + "\\data_cai.jsonl"
        self.game_chat_record = data_game + "\\data_chat_record.json" #record 在 streamlit平台上显示的数据
        self.game_send = data_game + "\\data_game_send.json" #向AI平台send的数据
        self.caiprompt = "请你根据用户的描述，猜出用户描述的词汇，请一步步分析，只需要返回你认为用户描述的事务，不需要解释原因。"
        self.jiangprompt = "现在正在进行一个猜词游戏，请你通过描述引导玩家猜词，可以提示玩家要猜的词汇有几个字，什么词性。"

    def choose_game(self) ->dict:
        '''
        选择一个题目
        '''
        data = []
        with open(self.game_question, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        random_item = random.choice(data)
        #记录所选题目
        with open(self.record_state, 'w', encoding='utf-8') as f:
            json.dump([random_item], f, ensure_ascii=False,indent=4)
        
        return random_item
    
    def delet_game_history(self):
        '''
        删除历史记录
        '''
        try:
            with open(self.game_chat_record, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            with open(self.game_send, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        except FileNotFoundError:
            pass
    
    def system_cai(self):
        '''
        写入ai为猜测时的system提示词
        '''
        with open(self.game_send, 'w', encoding='utf-8') as f:
            json.dump([
                {"role": "system", "content": self.caiprompt}
            ], f, ensure_ascii=False, indent=4)

    def user_cai(self):
        '''
        写入user为猜测时的user提示词
        '''
        with open(self.game_send, 'w', encoding='utf-8') as f:
            json.dump([
                {"role": "user", "content": self.jiangprompt}
            ], f, ensure_ascii=False, indent=4)

    def system_miaoshu(self):
        '''
        写入ai为描述时的system提示词
        '''
        with open(self.game_send, 'w', encoding='utf-8') as f:
            json.dump([
                {"role": "system", "content": self.jiangprompt}
            ], f, ensure_ascii=False, indent=4)

    def record_streamlit(self, message:str, role: str = Literal["S", "assistant", "user"]):
        '''
        记录在 streamlit 平台上的系统提示与对话
        '''
        with open(self.game_chat_record, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.append({"role": role, "content": message})
        
        with open(self.game_chat_record, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def streamlit_show(self) -> List:
        '''
        为streamlit 输出历史记录返回变量
        '''
        with open(self.game_chat_record, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def jiance_prompt(self, message:str):
        '''
        检测在描述的过程中是否违规
        '''
        with open(self.record_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        aim = data[0]["题目"]
        for item in list(aim):
            if item in message:
                return True
        return False
    
    def jiance_result(self, message:str):
        '''
        检测是否已经将词猜出
        '''
        with open(self.record_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data[0]["题目"] in message:
            return True
        else:
            return False
        
    def ai_miaoshu_first(self):
        '''
        用来配置user作为猜测者时，第一轮的prompt
        '''
        with open(self.record_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        timu = data[0]["题目"]

        prompt = f"请你以简略的语言描述“{timu}”，来引导玩家猜测出你所描述的事物。"
        
        proc_str = ""
        for item in timu:
            proc_str += f"{item}  "
        
        prompt = prompt + f"不要出现: “{proc_str}”中的任意一个字。以“我的描述是：”开头"

        with open(self.game_send, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.append({"role": "user", "content": prompt})
        with open(self.game_send, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def jiance_ai_jiang(self, message:str)-> Tuple[bool, str]:
        '''
        检测ai在进行描述的过程中是否出现违规并进行处理
        '''
        with open(self.record_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        aim = data[0]["题目"]
        new_message = ""
        flag = False
        for item in list(message):
            if item in aim:
                flag = True
                new_message += "()"
            else:
                new_message += item
        return flag, new_message
    
    def duti(self) -> str:
        '''
        读取题目
        '''
        with open(self.record_state, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[0]["题目"]


   
       



