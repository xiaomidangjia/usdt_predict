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
import matplotlib
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.font_manager import FontProperties  
#import matplotlib.text.Text
from matplotlib import font_manager as fm, rcParams
import matplotlib.pyplot as plt
import seaborn as sns
from dingtalkchatbot.chatbot import DingtalkChatbot
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=69d2f134c31ced0426894ed975f29b519c1a8bd163a808840ef5812c5a0477a1'
from qiniu import Auth, put_file, etag
def gmt_img_url(key=None,local_file=None,**kwargs):
    # refer:https://developer.qiniu.com/kodo/sdk/1242/python
    # key:上传后保存的文件名；
    # local_file:本地图片路径，fullpath
    # 遗留问题：如果服务器图片已存在，需要对保存名进行重命名

    #需要填写你的 Access Key 和 Secret Key
    access_key = 'svjFs68isTvptqveLl9xBADP9v8s0jZdUzoGe0-U'
    secret_key = 'XRqt6RgoeK9-hZmKyPjPuFQkeYcU0cPNVgKWEl7l'

    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'carsonlee'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key)

    #要上传文件的本地路径
    ret, info = put_file(token, key, local_file)

    base_url = 'http://ruusug320.hn-bkt.clouddn.com'    #七牛测试url
    url = base_url + '/' + key
    #private_url = q.private_download_url(url)

    return url
#fpath = os.path.join(rcParams["datapath"], "fonts/ttf/cmr10.ttf")
prop = fm.FontProperties(fname='/root/usdt_predict/SimHei.ttf')

# ======= 正式开始执行

# 读取原始数据
date_now = str(datetime.datetime.utcnow())[0:10]
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

    plt.savefig('未来24小时BTC价格趋势预测.jpg',  bbox_inches='tight')
    plt.close()

    from watermarker.marker import add_mark
    add_mark(file = "未来24小时BTC价格趋势预测.jpg", out = "out",mark = "0XCarson出品", opacity=0.2, angle=30, space=30)


    import telegram
    fig_name = '/root/usdt_predict/out/未来24小时BTC价格趋势预测.jpg'
    bot = telegram.Bot(token='6219784883:AAE3YXlXvxNArWJu-0qKpKlhm4KaTSHcqpw')


    bot.sendDocument(chat_id='-840309715', document=open(fig_name, 'rb'))
    #bot.sendMessage(chat_id='-840309715', text=text)


    #推送钉钉群

    time_str = str(time.time())[0:10]
    key = 'usdt_pre_' + time_str + '.png'
    img_url = gmt_img_url(key=key, local_file=fig_name)

    xiaoding = DingtalkChatbot(webhook)

    txt = '【未来24小时BTC价格趋势预测】 @所有人\n' \
          '> 说明：%s \n\n'\
          '> ![数据监控结果](%s)\n'\
          '> ###### 币coin搜索0xCarson,关注OKX实盘。 \n'%('红色线超出部分就是BTC价格趋势预测',img_url)
    xiaoding.send_markdown(title='数据监控', text=txt)
else:
    print('再来')






