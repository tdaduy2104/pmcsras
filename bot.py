import telegram
from flask import Flask, request

bot_token = "1205202424:AAFCLsQFwEjSsaeCuEBvNXZ3EmGMJEzgR_M"
bot_user_name = "pmcsqlbot"
URL = "https://pmcsras.herokuapp.com/"

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


def load_file(filename):
    with open(filename, "r") as file:
        lst = file.read().split('\n')
    return lst

app = Flask(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    text = update.message.text.encode('utf-8')
    access_list = ['-431936180', '-418484865', '1157659215']
    print("got text message :", text)

    if str(chat_id) in access_list:
        if text == "/start":
            msg = "Welcome to SQL Results Automation Subscribe system!!! Enter '/help' for all the command"
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif text == "/sendnudes":
            msg = 'First Header  | Second Header' \
                  '------------- | -------------' \
                  'Content Cell  | Content Cell'
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.MARKDOWN_V2)

        elif text == "/help":
            msg = "----All the command----\n" \
                  "/runall - run all sql query\n" \
                  "/run:{name} - run one sql query\n" \
                  "/showsql - list all sql\n" \
                  "/addsql:{name};{query} - add a new sql query\n" \
                  "/delsql:{name} - delete an existing sql\n" \
                  "/upsql:{name};{query} - update an existing sql\n" \
                  "/settime:{time} - run all sql at some time every day\n" \
                  "/settime:{dayinweek};{time} - run all sql at some time every specific day\n" \
                  ""
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
        else:
            msg = "Command not found! Show all command with /help."
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
    else:
        msg = "Hạ đẳng! Bạn không có cửa nói chuyện với tôi!"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

    return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
    app.run(threaded=True)
