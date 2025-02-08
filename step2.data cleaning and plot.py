from pathlib import Path
import json
import pandas as pd
import os
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt


def gross_clean():
    gamb_data = pd.read_csv('Gambling_features.csv',encoding='gbk',index_col=0)
    index_name = list(gamb_data.index)
    unknown_words = ['未提及', '不详', '未明确', '未提供','未知', '无', '不明', '不明确']
    pattern = '|'.join(map(re.escape, unknown_words))  # 使用 | 连接所有单词，确保特殊字符被转义
    gamb_data = gamb_data.replace(pattern, '不详', regex=True)
    gamb_data = gamb_data.replace(r'不详.*', '不详', regex=True)
    gamb_data = gamb_data.replace(r'.*不详', '不详', regex=True)
    gamb_data = gamb_data.fillna('不详')
    gamb_data.index = index_name
    gamb_data.loc['投稿时间（年月日时）',:] = [gamb_data.columns[i][:6] for i in range(len(gamb_data.columns))]
    
    gamb_data.to_csv('Gambling_features_clean.csv')


loan_data = pd.read_csv('Figure_contents.csv',index_col=0)
gamb_data = pd.read_csv('Gambling_features_clean.csv',index_col=0)

sns.set(font='SimHei',style='ticks')

'''
赌狗特征
'''


for feature in gamb_data.index[1:]:
    tmp =  pd.DataFrame(gamb_data.loc[feature,:])
    tmp = tmp[tmp[feature]!='不详']
    
    plt.figure(figsize=[4,int(len(np.unique(tmp[feature]))/5)])
    sns.countplot(data = tmp,
                y = feature)
    plt.title(feature)
    # plt.title('赌狗学历分布')
    # plt.savefig(f'media/academic_level.png',bbox_inches='tight',facecolor='w')
    plt.show()


plt.figure(figsize=[4,6])
sns.countplot(data = loan_data[loan_data['投稿人性别'].isin(['男','女'])],
             x = '投稿类型',hue='投稿人性别')
plt.show()

