import json
import os



def txt_record(data_his_path: str, data_txt_record_path: str) -> None:
    '''
    这个函数，用来将对话的历史记录导出为txt

    data_his_path 问历史文件储存的位置 .json
    data_txt_record_path 储存txt文件的文件夹路径
    '''

    system_list = []
    user_assistant_text = []


    try:
        with open(data_his_path, 'r',encoding='utf-8') as file:
            data = json.load(file)
        #print(data)
    except FileNotFoundError:
        print("文件不存在")

    for item in data:
        if item['role'] == 'system':
            system_list.append(item['content'])
        if item['role'] == 'user':
            user_assistant_text.append(item['content'])
        if item['role'] == 'assistant':
            user_assistant_text.append(item['content'])
    

    # 写入文本内容到.txt文件
    file_list = os.listdir(data_txt_record_path)

    txt_file_name = [file for file in file_list if file.endswith('.txt')]

    i = 0
    while "data_his_record" + str(i) + ".txt" in txt_file_name:
        i += 1

    
    with open(os.path.join(data_txt_record_path, "data_his_record" + str(i) + ".txt"), 'w',encoding='utf-8') as file:
        for item in system_list:
            file.write("对话背景设置：" + item.replace("\n\n",'\n') + "\n")
        file.write("\n")
        flag = True
        for item in user_assistant_text:
            if flag:
                file.write("用户：" + item.replace("\n\n",'\n') + "\n\n")
            else:
                file.write("AI助手：" + item.replace("\n\n",'\n') + "\n\n")
            flag = not flag
    print("文本写入成功")
