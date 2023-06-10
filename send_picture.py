import telegram
bot = telegram.Bot(token='6219784883:AAE3YXlXvxNArWJu-0qKpKlhm4KaTSHcqpw')
bot.sendDocument(chat_id='-840309715', document=open('/root/usdt_predict/out/未来24小时BTC价格趋势预测.png', 'rb'))