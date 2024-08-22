from enum import Enum
import logging
from mailbox import Message
import telegram
import yaml
from telegram.constants import ParseMode
from telegram import Bot

from bewegungskalender.output.message import MultiFormatMessage

class Channel():
    def __init__(self, id:str, botToken:str, type:str = ['prod', 'test']) -> None:
        self.id = id
        self.botToken = botToken
        self.type = type
        
def bot(token:str) -> Bot:
    """
    get a Telegram Bot object with token from config
    """
    bot:telegram.Bot = Bot(token=token)
    return bot

async def get_telegram_updates(config:dict):
    """
    telegram helper method to retrieve group_ids of groups that the bot joined
    """
    logging.debug('Getting telegram updates...')
    updates = await bot(config).get_updates()
    return "\n".join([str(u) for u in updates])

async def send_or_edit_telegram(channel:Channel, localdir:str, message:MultiFormatMessage, mode:str = ['edit', 'send']) -> None:
    if len(message) > 8000: # Check if message is too long for telegram
        logging.exception(f"Could not send message with {len(message)} characters to telegram, message longer than 8000 characters. Aborting."); exit(1)
    try:
        with open(f"{localdir}/lastmessage_{channel.type}.yml", "r+") as f:     
            if mode == 'send':
                logging.info('Sending Message to Telegram Channel...')
                lastmessage:dict = await bot(channel.botToken).send_message(text=message.markdown, 
                                                                chat_id=channel.id, 
                                                                parse_mode=ParseMode.MARKDOWN_V2, 
                                                                disable_web_page_preview=True)      
                f.write(f"id: {lastmessage.message_id}\n content: '{message.markdown}'") # write message_id of the message sent to file to be able to edit it
                logging.info(f"Succesfully sent message to Telegram Channel {channel.id}!")
            elif mode == 'edit':
                logging.info('Editing last Message in Telegram Channel...')
                lastmessage:dict = yaml.load(f, Loader=yaml.FullLoader)
                #TODO this doesnt work because message.txt is not actually txt format but markdown. 
                # For now changed stored content above to message.markdown
                if lastmessage['content'] != message.markdown:
                    await bot(channel.botToken).edit_message_text(text=message.markdown, 
                                            message_id=lastmessage['id'], 
                                            chat_id=channel.id, 
                                            parse_mode=ParseMode.MARKDOWN_V2, 
                                            disable_web_page_preview=True)    
                    logging.info(f"Succesfully edited last message in Telegram Channel: {channel.id}!")
                else:
                    logging.debug("Message has not changed since the last edit. No changes applied.")
    except telegram.error.TelegramError and telegram.error.BadRequest: # if something goes wrong
        logging.exception(f"Something went wrong while working in mode '{mode}' in telegram channel: {channel.type} - Aborting, please try again.\n")
        logging.exception(telegram.error.TelegramError, telegram.error.BadRequest)
        logging.debug(message)
    except FileNotFoundError:
        logging.exception(f"{localdir}/message_ids.yml: File with message_ids not Found"); exit()
    return
     
 