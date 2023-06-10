import telegram
bot = telegram.Bot(token='6219784883:AAE3YXlXvxNArWJu-0qKpKlhm4KaTSHcqpw')
bot.sendDocument(chat_id='-840309715', document=open('/root/usdt_predict/out/未来24小时BTC价格趋势预测.png', 'rb'))

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


#推送钉钉群

time_str = str(time.time())[0:10]
key = 'usdt_pre_' + time_str + '.png'
img_url = gmt_img_url(key=key, local_file='/root/usdt_predict/out/未来24小时BTC价格趋势预测.png')

xiaoding = DingtalkChatbot(webhook)

txt = '【未来24小时BTC价格趋势预测】 @所有人\n' \
      '> 说明：%s \n\n'\
      '> ![数据监控结果](%s)\n'\
      '> ###### 币coin搜索0xCarson,关注OKX实盘。 \n'%('红色线超出部分就是BTC价格趋势预测',img_url)
xiaoding.send_markdown(title='数据监控', text=txt)