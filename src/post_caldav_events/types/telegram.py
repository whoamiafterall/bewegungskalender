def bot(config):
    """
    get a Telegram Bot object with token from config
    """
    from telegram import Bot
    bot = Bot(token=config['output']['token'])
    return bot

def get_updates():
    """
    telegram helper method to retrieve group_id
    """
    updates = bot.get_updates()
    return "\n".join([str(u) for u in updates])

def send(config, message):
    from telegram import ParseMode
    print(message)
    file1 = open('message.txt', 'w')
    file1.write(message)
    file1.close()
    if len(message) < 9500:
        bot(config).send_message(text=message, chat_id=config['output']['group_id'], parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
    else:
        print (len(message))
    return
