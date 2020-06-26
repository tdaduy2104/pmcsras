import logging
import random

from telegram.ext import Updater, CommandHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
TOKEN = "844716509:AAHypcTWAuLf2raqKl7xuiCYqc698gKrmWs"

#local
# def run(updater):
#     updater.start_polling()

#deploy
def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook("https://pmcsras.herokuapp.com/{}".format(TOKEN))


def start_handler(bot, update):
    # Creating a handler-function for /start command
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello from Python!\nPress /random to get random number")

def random_handler(bot, update):
    # Creating a handler-function for /random command
    number = random.randint(0, 10)
    logger.info("User {} randomed number {}".format(update.effective_user["id"], number))
    update.message.reply_text("Random number: {}".format(number))

def callback_alarm(bot, job):
    bot.send_message(chat_id=job.context, text='Alarm')

def callback_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Starting!')
    job_queue.run_repeating(callback_alarm, 5, context=update.message.chat_id)

def stop_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Stoped!')
    job_queue.stop()

if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start_handler))
    updater.dispatcher.add_handler(CommandHandler('random', random_handler))
    updater.dispatcher.add_handler(CommandHandler('trigger', callback_timer, pass_job_queue=True))
    updater.dispatcher.add_handler(CommandHandler('stop', stop_timer, pass_job_queue=True))

    run(updater)
