def bot(config):
    """
    get a Telegram Bot object with token from config
    """
    from telegram import Bot
    bot = Bot(token=config['telegram']['token'])
    return bot

def get_telegram_updates(config):
    """
    telegram helper method to retrieve group_ids of groups that the bot joined
    """
    updates = bot(config).get_updates()
    return "\n".join([str(u) for u in updates])

def send_telegram(config, telegram_id, message):
    from telegram import ParseMode
    if len(message) < 9500:
        bot(config).send_message(text=message, chat_id=telegram_id, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
    else:
        print (len(message))
    return
