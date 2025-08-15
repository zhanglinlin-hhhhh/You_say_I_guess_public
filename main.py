import streamlit as st
import gamecai
from package import zhipu as zp
from package import dealJson as dj
from typing import Tuple,Literal,List
import json


st.title("Human LLM You Say I Guess 😊")


class platform():
    def __init__(self,data_path_plat ,data_game_path):
        '''
        data_path_plat 储存平台文件的文件夹，不带文件名称
        data_game_path 谁是卧底游戏的文件路径
        '''
        self.chat_his = data_path_plat + "/data_his.json"
        self.get_pcm = data_path_plat + "/get.pcm"
        self.demo_pcm = data_path_plat + "/demo.pcm"
        self.out_his = data_path_plat
        self.data_game = data_game_path
        self.data_chat_state = data_path_plat + "/data_record_state.json"
        self.data_api = data_path_plat + "/data_api.json" #用来获取模型调用的api参数

    def read_chat_state(self) -> List: #读取聊天历史状态
        '''
        读取对话的历史状态
        '''
        state_record  = dj.read_history_json(self.data_chat_state)
        if state_record == []:
            state_record = [
                {
                    "picture_input": False,
                    "game_state": False,
                    "gaming": False
                }
            ]
        return state_record
    
    def read_chat_history(self)->List:
        '''
        读取对话的历史信息
        '''
        chat_his = dj.read_history_json(self.chat_his)
        return chat_his

    
    def modify_state_rerun(self,state_record:List):
        '''
        在断点处记录平台状态，用于刷新界面
        必须要传入，平台目前的 state_record
        '''
        with open(self.data_chat_state, 'w', encoding='utf-8') as f:
            json.dump(state_record, f, ensure_ascii=False, indent=4)
        st.rerun()

def show_chat(data:List):
    '''
    用来展示多轮对话
    '''
    for item in data:
        if item["role"] == "S":
            st.chat_message(item["role"],avatar="😊").write(item["content"])
        else:
            st.chat_message(item["role"]).write(item["content"])


def cai_show_record(prompt:str, role:str = Literal["S","user","assistant"] ):
    '''
    用来在你说我猜游戏中，方便进行展示与记录
    '''
    if role == "S":
        st.chat_message(role,avatar="😊").write(prompt)
    else:
        st.chat_message(role).write(prompt)
    game_cai.record_streamlit(prompt,role)


data_path_plat = r"F:\plat\data"
data_game = r"F:\plat\data_who"

# class 类的定义与使用
plat = platform(data_path_plat ,data_game)

state_record = plat.read_chat_state()

# 你说我猜 游戏定义
game_cai = gamecai.gamenishuowocai(r"F:\plat\data_cai")

shenfen = st.sidebar.selectbox("请选择你的身份",["描述者","猜测者"])

#点击开始游戏
if st.sidebar.button("开始游戏 🎈"):
    game_cai.delet_game_history() # 去除历史记录
    state_record[0]["gaming"] = True 
    question = game_cai.choose_game()
    ci = question["题目"]

    if shenfen == "描述者":
        game_cai.system_cai()
        system_prompt = f"你要描述的词是“{ci}”"
        game_cai.record_streamlit(system_prompt,"S")

    elif shenfen == "猜测者":
        game_cai.user_cai()
        system_prompt = f"你的角色是猜词，请根据AI给出的提示进行猜测"
        game_cai.record_streamlit(system_prompt,"S")
        game_cai.ai_miaoshu_first()
        answer = zp.zhipu_send_get_only(plat.data_api,game_cai.game_send,"glm-4")
        flag,new_str = game_cai.jiance_ai_jiang(answer)
        if flag:
            game_cai.record_streamlit("AI的描述出现违规，已将违规的词处理","S")
            game_cai.record_streamlit(new_str,"assistant")
        else:
            game_cai.record_streamlit(answer,"assistant")


if state_record[0]["gaming"] == True: # 游戏状态

    out = game_cai.streamlit_show()
    show_chat(out)

    if shenfen == "描述者":
        # 文字输入
        if  prompt := st.chat_input():
            cai_show_record(prompt,"user")
            # 检测，提示词是否违规
            if game_cai.jiance_prompt(prompt):
                cai_show_record("描述违规本轮此作废","S")
            else:
                answer, lunshu = zp.get_zhipu_text(plat.data_api,prompt,game_cai.game_send,"glm-4.5-flash")
                cai_show_record(answer,"assistant")
                num = int(2-lunshu)
                
                # 检测结果是否被猜出
                if game_cai.jiance_result(answer):
                    st.chat_message("S").write("成功了。点击左侧“开始游戏”进行下一轮")
                else:
                    if num == 0:
                        st.chat_message("S").write("很遗憾AI没有猜出来。点击左侧“开始游戏”进行下一轮")
                        state_record[0]["gaming"] = False
                    else:
                        system_prompt = f"剩余轮数{num}"
                        cai_show_record(system_prompt,"S")

    # 当由 AI描述 user猜测时
    elif shenfen == "猜测者":
        # 文字输入
        timu = game_cai.duti()
        if  caice := st.chat_input():
            cai_show_record(caice,"user")
            # 检测结果是否被猜出
            if game_cai.jiance_result(caice):
                st.chat_message("S").write("成功了。点击左侧“开始游戏”进行下一轮")
            else:
                input_text= f"玩家描述为：{caice}，并没有猜对，请你根据历史信息继续引导玩家猜测“{timu}”。"
                answer,lunshu = zp.get_zhipu_text(plat.data_api,input_text,game_cai.game_send,"glm-4.5-flash")
                flag,new_str = game_cai.jiance_ai_jiang(answer)
                if flag:
                    game_cai.record_streamlit("AI的描述出现违规，已将违规的词处理","S")
                    game_cai.record_streamlit(new_str,"assistant")
                else:
                    game_cai.record_streamlit(answer,"assistant")
                num = int(4-lunshu)

                if num == 0:
                    timu = game_cai.duti()
                    st.chat_message("S").write(f"很遗憾没有猜出来,“{timu}”为要猜测的词。点击左侧“开始游戏”进行下一轮")
                    state_record[0]["gaming"] = False
                else:
                    system_prompt = f"剩余轮数{num}"
                    cai_show_record(system_prompt,"S")
                    st.rerun()


if st.sidebar.button("结束游戏 👌"):
    state_record[0]["gaming"] = False
    game_cai.delet_game_history()
    plat.modify_state_rerun(state_record)

######对历史记录进行重写
with open(plat.data_chat_state, 'w',) as file:
    json.dump(state_record, file,indent=4, ensure_ascii=False)

st.sidebar.info("""### **你说我猜**

**基本规则：**

* **角色分配：** 两名玩家，一人负责**说**，一人负责**猜**。
* **游戏内容：** “说”的玩家会拿到一个词语，他必须用**语言**来描述这个词语，但**不能直接说出这个词语本身或其中的任何一个字**。
* **游戏目标：** “猜”的玩家需要根据描述，在规定的时间内尽可能多地猜出正确的词语。

**举例说明：**

* **词语：** "苹果"
* **说者描述：** "这是一种水果，是红色的，可以榨汁喝，有个著名的手机公司用它做商标。"
* **猜者回答：** "苹果！" """)