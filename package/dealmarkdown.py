

def double_br(text):
    if "<br><br>" in text:
        text = text.replace("<br><br>", "<br>")
    return text

def if_hengxian(text,  ziti = "FangSong" , zihao = "12pt"):
    add_text = "<span style='font-family:" + ziti + "; font-size:" + zihao + "pt'>"
    if "\n-" in text:
        text = text.replace("\n-", "<br>&nbsp;&nbsp;&nbsp;&nbsp;&bullet;" + add_text)
    return text
    
#最后处理    
def ai_head(text):
    text = "<span style='font-family:Times New Roman; font-size:14pt'>AI</span><br>" + text
    return text

def huahang_sub(text):
    if "\n" in text:
        text = text.replace("\n", "<br>&nbsp;&nbsp;&nbsp;&nbsp;")
        text = double_br(text)
    return text

def huahang_double(text):
    if "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text

def math(text, ziti = "FangSong" , zihao = "12pt"):
    add_text = "<span style='font-family:" + ziti + "; font-size:" + zihao + "pt'>"
    if "\(" in text:
        text = text.replace("\\(", "$")
        text = text.replace("\\)", "$")
        text = text.replace("\(", "$")
        text = text.replace("\)", "$")
    if "\[" in text:
        text = text.replace("\\[", "<br><center>$")
        text = text.replace("\\]", "$</center>" + add_text)
        text = text.replace("\[", "<br><center>$")
        text = text.replace("\]", "$</center>" + add_text)
    return text





def Fangsong_12pt_AI(text):

    text = "<span style='font-family:FangSong; font-size:12pt'>&nbsp;&nbsp;&nbsp;&nbsp;" + text + "</span>"
    
    text = huahang_double(text)

    text = if_hengxian(text)

    text = huahang_sub(text)
    
    text = math(text)

    text = double_br(text)
    
    print(repr(text))
    return ai_head(text)
    


def Arial_12pt_AI(text):

    text = "<span style='font-family: Arial; font-size:12pt'>&nbsp;&nbsp;&nbsp;&nbsp" + text + "</span>"
    text = "<span style='font-family:Times New Roman; font-size:14pt'>AI:</span><br>" + text

    if "\n" in text:
        if "\n\n" in text:
            text = text.replace("\n\n", "</span><br><span style='font-family: Arial; font-size:12pt'>&nbsp;&nbsp;&nbsp;&nbsp")
        else:
            text = text.replace("\n", "</span>\<br><span style='font-family: Arial; font-size:12pt'>&nbsp;&nbsp;&nbsp;&nbsp")
    
    return text
