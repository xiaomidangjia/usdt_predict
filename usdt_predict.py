import json
import requests
import pandas as pd
import time
import numpy as np
import os
import re
from tqdm import tqdm
import datetime
#=====定义函数====
#from HTMLTable import HTMLTable
import os, sys
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.font_manager import FontProperties  
#import matplotlib.text.Text
from matplotlib import font_manager as fm, rcParams
import matplotlib.pyplot as plt
import seaborn as sns

# ======= 正式开始执行
prop = fm.FontProperties(fname='/root/usdt_predict/SimHei.ttf')
# 读取原始数据
date_now = datetime.datetime.utcnow()
date_before = pd.to_datetime(date_now) - datetime.timedelta(days=8)
# 读取原始数据
raw_data = pd.read_csv('/root/usdt/usdt.csv')
raw_data = raw_data[2:]
raw_data['date'] = raw_data['date'].apply(lambda x: str(x)[6:10] + '/' + str(x)[3:5] + '/' + str(x)[0:2] + ' ' + str(x)[11:19])
raw_data['date'] = pd.to_datetime(raw_data['date'])
raw_data['date'] = raw_data['date'] - datetime.timedelta(hours=8)
#取最近7天的数据
raw_data = raw_data[(raw_data.date >= date_before) & (raw_data.date < date_now)]
raw_data['date_dd'] = raw_data['date'].apply(lambda x: str(x)[0:10])
raw_data['date_hh'] = raw_data['date'].apply(lambda x: str(x)[11:13])
raw_data['per'] = raw_data['usdt']/raw_data['usd']
raw_data = raw_data[['date_dd','date_hh','per']]
raw_data = raw_data.drop_duplicates()
raw_data = raw_data.groupby(['date_dd','date_hh'],as_index=False)['per'].mean()

raw_data = raw_data.sort_values(by=['date_dd','date_hh'])
raw_data = raw_data.reset_index(drop=True)
raw_data['per_1'] = raw_data['per'].shift(1)
raw_data['per_2'] = raw_data['per'].shift(2)
raw_data = raw_data.fillna(0)
per_last = []
for i in range(len(raw_data)):
    #print(i,raw_data['per'][i])
    if raw_data['per'][i] > 0:
        per_last.append(raw_data['per'][i])
    elif raw_data['per'][i] == 0:
        per_last.append(raw_data['per_1'][i])
    elif raw_data['per_1'][i] == 0:
        per_last.append(raw_data['per_2'][i])
    else:
        per_last.append(raw_data['per'][i])
raw_data['per_last'] = per_last
raw_data = raw_data[['date_dd','date_hh','per_last']]

#启用价格
url_address = ['https://api.glassnode.com/v1/metrics/market/price_usd_close']
url_name = ['Price']
# insert your API key here
API_KEY = '26BLocpWTcSU7sgqDdKzMHMpJDm'
data_list = []
for num in range(len(url_name)):
    addr = url_address[num]
    name = url_name[num]
    # make API request
    res_addr = requests.get(addr,params={'a': 'BTC','i':'1h', 'api_key': API_KEY})
    # convert to pandas dataframe
    ins = pd.read_json(res_addr.text, convert_dates=['t'])
    ins['date'] =  ins['t']
    ins[name] =  ins['v']
    ins = ins[['date',name]]
    data_list.append(ins)

result_data = data_list[0][['date']]
for i in range(len(data_list)):
    df = data_list[i]
    result_data = result_data.merge(df,how='left',on='date')
#last_data = result_data[(result_data.date>='2016-01-01') & (result_data.date<='2020-01-01')]
last_data = result_data[(result_data.date>='2023-05-01')]
last_data = last_data.sort_values(by=['date'])
last_data = last_data.reset_index(drop=True)
last_data['date_dd'] = last_data['date'].apply(lambda x: str(x)[0:10])
last_data['date_hh'] = last_data['date'].apply(lambda x: str(x)[11:13])
next_df = raw_data.merge(last_data,how='left',on=['date_dd','date_hh'])
next_df = next_df[next_df.date >= '2023-06-02']
next_df = next_df.reset_index(drop=True)
date = []
price = []
yijia = []
num = 4
for i in range(num,len(next_df)):
    ins = next_df[i-num:i]
    ins = ins.sort_values(by=['date'])
    ins = ins.reset_index(drop=True)
    date.append(ins['date'][num-1])
    price.append(ins['Price'][num-1])
    yijia.append(np.mean(ins['per_last']))
test_df = pd.DataFrame({'date':date,'price':price,'yijia':yijia}) 

num = []
corr = []
for i in range(4,48):
    name1 = 'yijia_' + str(i)
    test_df[name1] = test_df['yijia'].shift(i) 
    name2 = 'date_' + str(i)
    test_df[name2] = test_df['date'].shift(i)     
    df = test_df.dropna()
    num.append(i)
    corr.append(np.corrcoef(list(df['price']),list(df[name1]))[0][1])

corr_df = pd.DataFrame({'num':num,'corr':corr})
corr_df = corr_df.sort_values(by='corr',ascending=False)
corr_df = corr_df.reset_index(drop=True)
corr_df = corr_df[0:3]
corr_df
flag = 0
for i in range(3):
    if corr_df['num'][i] in (22,23,24) and corr_df['corr'][i] > 0.7:
        flag += 1
    else:
        flag += 0
if flag > 0 and len(raw_data) > 153:
    test_df_1 = test_df[test_df.date>test_df['date_23'][len(test_df)-1]]
    test_df_1['new_date'] = pd.to_datetime(test_df_1['date']) + datetime.timedelta(hours=23)
    test_df_2 = test_df_1[['new_date','yijia']]
    date_max_min = list(test_df_2['new_date'])
    yijian_max_min = list(test_df_2['yijia'])

    max_value_time = date_max_min[yijian_max_min.index(max(yijian_max_min))]
    min_value_time = date_max_min[yijian_max_min.index(min(yijian_max_min))]
    time_now = datetime.datetime.utcnow()
    max_min_df = pd.DataFrame({'time_now':time_now,'max_value_time':max_value_time,'min_value_time':min_value_time},index=[0])
    max_min_df.to_csv('usdt_24.csv',index=False)
    #======制定第4区域

    test_df = test_df[['date','price','yijia']]
    test_df_yijia = test_df[['date','yijia']]
    test_df_yijia['date'] = test_df['date'] + datetime.timedelta(hours=23)
    test_df_price = test_df[['date','price']]
    next_df = test_df_yijia.merge(test_df_price,how='left',on=['date'])
    import matplotlib.pyplot as plt
    import seaborn as sns
    f, axes = plt.subplots(figsize=(20, 10))
    axes_fu = axes.twinx()

    sns.lineplot(x="date", y="price", data=next_df, color = 'black', linewidth=0.5,ci=95, ax=axes)
    sns.lineplot(x="date", y="yijia",color='red', linewidth=0.5,data=next_df, ci=95, ax=axes_fu)
    plt.title('未来24小时BTC价格趋势预测', fontsize=20,fontproperties=prop) 
    axes.set_xlabel('时间',fontsize=14,fontproperties=prop)
    axes.set_ylabel("BTC价格",fontsize=14,fontproperties=prop)
    axes_fu.set_ylabel("BTC价格趋势",fontsize=14,fontproperties=prop)

    plt.savefig('未来24小时BTC价格趋势预测.png',  bbox_inches='tight')
    plt.close()

    from watermarker.marker import add_mark
    add_mark(file = "未来24小时BTC价格趋势预测.png", out = "out",mark = "币coin---0XCarson出品", opacity=0.2, angle=30, space=30)


else:
    print('再来')



