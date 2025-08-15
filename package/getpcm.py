# -*- coding:utf-8 -*-
# author: Ysh
#这个库用来处理pcm音频文件


import sounddevice as sd
import numpy as np
import time
import streamlit as st
from typing import List


def get_pcm(file_path: str, flag: bool = 'none', duration: int = 10) -> None:

    '''
    驱动电脑进行录音，并将文件保存为.pcm文件
    file_path为需要传入的 文件路径与名称 
    flag用来选择是否 选用streamlit模式
    duration 为录音时长 默认的时长为10s
    '''
    
    # 设置录音的参数
    fs = 16000  # 采样率
    channels = 1  # 单声道

    if flag == "streamlit":
    
        # 开始录音
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
        time.sleep(1)
        with st.spinner('speaking'):
        # 等待录音结束
            sd.wait()
    
    if flag == "none":
        # 开始录音
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
        time.sleep(1)
        print("开始录音，录音时长{}秒".format(duration))
        # 等待录音结束
        sd.wait()
        print("录音结束")

    # 将录音数据转换为16位整数
    myrecording = np.int16(myrecording * 32767)

    # 保存录音数据为.pcm文件
    with open(file_path, 'wb') as f:
        f.write(myrecording.tobytes())


        

        
def play_pcm(file_path: str) ->None:

    '''
    驱动电脑进行对生成的.pcm文件进行播放

    file_path为需要传入的 文件路径与名称 
    '''

     # 设置播放的参数
    fs = 16000  # 采样率
    

    # 读取.pcm文件
    with open(file_path, 'rb') as f:
        buf = f.read()

    # 将数据转换为numpy数组
    data = np.frombuffer(buf, dtype=np.int16)

    # 播放音频
    print("开始播放")
    sd.play(data / 32767, samplerate=fs)

    # 等待播放结束
    sd.wait()
    print("播放结束")