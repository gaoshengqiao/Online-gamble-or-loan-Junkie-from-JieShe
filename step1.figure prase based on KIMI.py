from openai import OpenAI
from pathlib import Path
import json
import pandas as pd
import os
client = OpenAI(
    api_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    base_url = "https://api.moonshot.cn/v1",
)

out_figure = pd.DataFrame()
out_gambling = pd.DataFrame()

figures = os.listdir('JieShe')

i=0
for figure in figures:
    try:
        file_object = client.files.create(file=Path(f"JieShe/{figure}"), purpose="file-extract")
    except:
        continue
    file_content = client.files.content(file_id=file_object.id).text
    messages_pre = [
    {
        "role": "system",
        "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
    },
    {
        "role": "system",
        "content": file_content, # <-- 这里，我们将抽取后的文件内容（注意是文件内容，而不是文件 ID）放置在请求中
    },
    {"role": "user", "content": "请根据图中内容提取三条特征'reply','total money','gender'，内容是否涉及赌博相关信息请在第一个reply特征里回复'赌博'，如果不涉及赌博仅涉及借贷，请回复'网贷'，否则请回复'其他'; 并在第二个total money特征里回复赌博或贷款涉及的金额（使用阿拉伯数字，具体金额或金额范围），第三个gender特征里填写投稿人性别，如果未提及上述特征，请填写'未提及'"},
    ]
    
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages = messages_pre,
        temperature=0.3,
        response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
    )
    content = json.loads(completion.choices[0].message.content)
    out_figure.loc[figure.split('.')[0],'投稿类型'] = list(content.values())[0]
    out_figure.loc[figure.split('.')[0],'欠款总额'] = list(content.values())[1]
    out_figure.loc[figure.split('.')[0],'投稿人性别'] = list(content.values())[2]
    
    print(f"第{i+1}张图，内容是{list(content.values())[0]}")
    
    if list(content.values())[0] == '赌博':
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
                },
                {
                    "role": "system",
                    "content": file_content, # <-- 这里，我们将抽取后的文件内容（注意是文件内容，而不是文件 ID）放置在请求中
                },
                {"role": "user", "content": "请提取以下特征，并做成数据库，特征用以下中文名称（不许修改或翻译）：'投稿时间（年月日时）'，'投稿人与赌博人的关系'，'赌博人性别'，'年龄'，'职业'，'社会地位'，'身体健康程度'，'家庭成员及职业'，'是否单亲/离异家庭'，'赌博人的负债'，'赌博被发现次数'，'赌博人学历'，'初赌年龄'，'初赌是否成年？'，'赌龄'，'最初赌博游戏'（网赌？线下赌博？），'初赌的输赢情况'，'是否提到世界杯/电竞？'，'赌博人债务来源'（网贷，家庭，朋友，同事），'赌博被发现或主动坦白的次数'，'赢钱后的消费方式'，'赌博人家庭初次发现赌博人赌博后的处理方式是什么'，'赌博人是否表现出自杀倾向'，'赌博人结局'。"},
            ]
            
            completion = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages = messages,
                temperature=0.3,
                response_format={"type": "json_object"}, # <-- 使用 response_format 参数指定输出格式为 json_object
            )
            content = json.loads(completion.choices[0].message.content)
            # print(completion.choices[0].message)

            tmp = pd.DataFrame(content.values(),index=content.keys() )
            tmp.columns = [figure.split('.')[0]]
            out_gambling = pd.concat([out_gambling,tmp],axis=1)
        except:
            continue
    i+=1
    if i%10 ==0:
        out_gambling.to_csv('Gambling_features_test.csv',sep=',')
        out_figure.to_csv('Figure_contents_test.csv',sep=',')
        
        file_list = client.files.list()
        for file in file_list.data:
            client.files.delete(file_id=file.id)
            
            
    
