import pyodbc
import sqlvalidator
import telegram
from flask import Flask, request

bot_token = "1205202424:AAFCLsQFwEjSsaeCuEBvNXZ3EmGMJEzgR_M"
bot_user_name = "pmcsqlbot"
URL = "https://pmctelebot.azurewebsites.net/"

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)


def run_query(query):

    authentication = 'ActiveDirectoryPassword'
    server = 'pharmacity.database.windows.net'
    database = 'PMC_DW'
    username = 'powerbishare1@pharmacity.vn'
    password = 'Pmc@1234'
    driver = '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER=' + driver +
                          ';SERVER=' + server +
                          ';DATABASE=' + database +
                          ';UID=' + username +
                          ';PWD=' + password +
                          ';AUTHENTICATION=' + authentication
                          )

    sql_query = query
    cursor = cnxn.cursor()
    cursor.execute(sql_query)
    cols = [cursor[0] for cursor in cursor.description]
    rows = [cursor[0] for cursor in cursor.fetchall()]
    return rows, cols

def load_file(filename):
    with open(filename, "r") as file:
        lst = file.read().split('\n')
    return lst

app = Flask(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    global chat_id, access_list, msg_id, text
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
        text = update.message.text.encode('utf-8')
        access_list = ['-431936180', '-418484865', '1157659215']
        print("got text message :", text)
    except:
        msg = "ERROR!"
        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

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
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)                  '*Content Cell*  | Content Cell' \


        elif "/settime:" in text:
            cmd = str(text.split(':')[-1])
            # Scheduler with day, time
            if ';' in cmd:
                time = cmd.split(';')[-1]
                day = cmd.split(';')[0]
            # Scheduler with time
            else:
                time = cmd

        elif text == "/runall":
            msg_lst = []
            lst_sql = load_file("sqlquery.txt")
            try:
                for id, line in enumerate(lst_sql):
                    query = str(line.split(';')[-1])
                    rows, cols = run_query(query)
                    for i in range(len(rows)):
                        tmp = str(cols[i]) + ': ' + str(rows[i])
                        msg_lst.append(tmp)
                msg = '\n'.join(str(m) for m in msg_lst)
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            except:
                msg = "@ERRPR: Oops, something went wrong, please try again!"
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif "/run:" in text:
            msg_lst = []
            query_name = str(text.split(':')[-1])
            try:
                lst_sql = load_file("sqlquery.txt")
                for id, line in enumerate(lst_sql):
                    name = line.split(';')[0]
                    query = line.split(';')[-1]
                    if query_name == name:
                        rows, cols = run_query(query)
                        for i in range(len(rows)):
                            tmp = str(cols[i]) + ': ' + str(rows[i])
                            msg_lst.append(tmp)
                        msg = '\n'.join(str(m) for m in msg_lst)
                        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                    else:
                        msg = 'Query not found, please check whether you input a correct name!!!'
                        bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            except:
                msg = '@ERRPR: Oops, something went wrong, please try again!'
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif "/addsql:" in text:
            text = text.replace('\n', '')
            query = text.split(':')[-1]
            lst_sql = load_file("sqlquery.txt")
            if query in lst_sql:
                msg = "@ERROR: This query already exists! Try add another one."
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            else:
                sql_query = query.split(';')[-1]
                if sqlvalidator.parse(sql_query).is_valid():
                    lst_sql.append(sql_query)
                    with open("sqlquery.txt", "w", encoding='utf8') as file:
                        file.write("\n".join(str(line) for line in lst_sql))
                    msg = f"SQL Query '{query.split(';')[0]}' added successfully!"
                    bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                else:
                    msg = "@ERROR: SQL query syntax error, please check whether you input the correct query!"
                    bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif text == "/showsql":
            try:
                lst_sql = load_file("sqlquery.txt")
                for id, line in enumerate(lst_sql):
                    lst_sql[id] = f'{id + 1}. ' + line
                msg = '\n'.join(str(line) for line in lst_sql)
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            except:
                msg = '@ERRPR: Oops, something went wrong, please try again!'
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif "/delsql:" in text:
            ifdel = False
            lst_sql = load_file("sqlquery.txt")
            name = str(text.split(':')[-1])
            for index, sql in enumerate(lst_sql):
                sql_name = str(sql.split(';')[0])

                if name == sql_name:
                    del lst_sql[index]
                    with open("sqlquery.txt", "w", encoding='utf8') as file:
                        file.write("\n".join(str(line) for line in lst_sql))
                    msg = f"{name} have been removed!"
                    bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                    ifdel = True
                    break

            if not ifdel:
                msg = f"{name} not exist, please make sure you type the correct query name!"
                bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)

        elif "/upsql:" in text:
            ifdel = False
            lst_sql = load_file("sqlquery.txt")
            name = str(text.split(':')[-1])
            for index, sql in enumerate(lst_sql):
                sql_name = str(sql.split(';')[0])
                bot.sendMessage(chat_id=chat_id, text=sql_name, reply_to_message_id=msg_id)

                if name == sql_name:
                    lst_sql[index] = text
                    with open("sqlquery.txt", "w", encoding='utf8') as file:
                        file.write("\n".join(str(line) for line in lst_sql))
                    msg = f"{name} have been updated!"
                    bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                    ifdel = True
                    break

            if not ifdel:
                msg = f"{name} not exist, please make sure you type the correct query name!"
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
