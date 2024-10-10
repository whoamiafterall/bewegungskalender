import telegram
import yaml
from telegram import Bot
from bewegungskalender.functions.logger import LOGGER
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
    telegram functions method to retrieve group_ids of groups that the bot joined
    """
    LOGGER.debug('Getting telegram updates...')
    updates = await bot(config).get_updates()
    return "\n".join([str(u) for u in updates])
    
async def send_or_edit_telegram(channel:Channel, localdir:str, message:MultiFormatMessage, edit:bool) -> None:
    if len(message.markdown) > 8000: # Check if message is too long for telegram
        LOGGER.exception(f"Could not send message with {len(message.markdown)} characters to telegram, message longer than 8000 characters. Aborting."); exit(1)
    try:
        with open(f"{localdir}/lastmessage.txt", "r+") as content:
            with open(f"{localdir}/message_ids.yml", "r+") as ids:
                last_msg_ids = yaml.load(ids, Loader=yaml.SafeLoader)
                if edit == False:
                    LOGGER.info('Sending Message to Telegram Channel...')
                    lastmessage:dict = await bot(channel.botToken).send_message(text=message.markdown, 
                                                                    chat_id=channel.id, 
                                                                    parse_mode="MarkdownV2", 
                                                                    disable_web_page_preview=True)      
                    content.seek(0), content.write(message.txt), content.truncate() # write message content to file to be able to check if it has changed
                    last_msg_ids[channel.type] = lastmessage.message_id
                    LOGGER.info(f"Succesfully sent message to Telegram Channel {channel.id}!")
                elif edit == True:
                    LOGGER.info('Editing last Message in Telegram Channel...')
                    if content.read() == message.txt:
                        LOGGER.info("Message has not changed since the last edit. No changes applied.")
                    else:
                        await bot(channel.botToken).edit_message_text(text=message.markdown, 
                                                message_id=last_msg_ids[channel.type], 
                                                chat_id=channel.id, 
                                                parse_mode="MarkdownV2", 
                                                disable_web_page_preview=True)    
                        content.seek(0), content.write(message.txt), content.truncate()
                        LOGGER.info(f"Succesfully edited last message in Telegram Channel: {channel.id}!")
                ids.seek(0); ids.write(yaml.dump(last_msg_ids, Dumper=yaml.SafeDumper)); ids.truncate()
    except telegram.error.TelegramError and telegram.error.BadRequest: # if something goes wrong
        LOGGER.exception(f"Something went wrong while working in telegram channel: {channel.type} - Aborting, please try again.\n")
        LOGGER.exception(telegram.error.TelegramError, telegram.error.BadRequest)
        LOGGER.debug(message)
    except FileNotFoundError:
        LOGGER.exception(f"{localdir}/message_ids.yml: File with message_ids not Found"); exit()
    return
     
 