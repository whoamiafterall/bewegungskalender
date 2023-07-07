def bot(config):
    """
    get a Telegram Bot object with token from config
    """
    from telegram import Bot
    bot = Bot(token=config['telegram']['token'])
    return bot

def get_telegram_updates():
    """
    telegram helper method to retrieve group_id
    """
    updates = bot.get_updates()
    return "\n".join([str(u) for u in updates])

def log_message(message):
    with open('post_caldav_events/logs/message.txt', 'w') as logfile:
        logfile.write(message)
        logfile.close()

def send_telegram(config, message):
    from telegram import ParseMode
    log_message(message)
    if len(message) < 9500:
        bot(config).send_message(text=message, chat_id=config['telegram']['group_id'], parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
    else:
        print (len(message))
    return
