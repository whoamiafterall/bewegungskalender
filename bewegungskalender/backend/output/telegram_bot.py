import yaml
from telegram._bot import Bot
from telegram.error import BadRequest

from bewegungskalender.backend.io.cli import TELEGRAM_CHANNEL, TELEGRAM_EDIT
from bewegungskalender.backend.io.config import DATADIR
from bewegungskalender.backend.io.credentials import TELEGRAM_TEST, TELEGRAM_TOKEN, TELEGRAM_PRODUCTION
from bewegungskalender.backend.io.file import safe_open
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.backend.formatting.message import MultiFormatMessage

bot:Bot = Bot(TELEGRAM_TOKEN)

def get_last_msg_ids() -> dict:
    with safe_open(f"{DATADIR}/message_ids.yml", "r") as ids:
        last_msg_ids = yaml.load(ids, Loader=yaml.SafeLoader)
        if last_msg_ids is None and TELEGRAM_EDIT:
            LOGGER.exception("It seems like there is no message that could be edited. Please try to send one first."); exit(1)
        elif last_msg_ids is None:
            last_msg_ids = {TELEGRAM_CHANNEL: 0}
        return last_msg_ids

async def get_telegram_updates():
        """
        telegram libs method to retrieve group_ids of groups that the bot joined
        """
        LOGGER.debug('Getting telegram updates...')
        updates = await bot.get_updates()
        return "\n".join([str(u) for u in updates])
    
async def send_or_edit_telegram(message:MultiFormatMessage) -> None:
    if len(message.markdown) > 8000: # Check if message is too long for telegram
        LOGGER.exception(f"Counted {len(message.markdown)} characters => Message too long. Limit = 8000 characters."); exit(1)
    channel_id = TELEGRAM_PRODUCTION if TELEGRAM_CHANNEL == 'prod' else TELEGRAM_TEST
    last_msg_ids:dict = get_last_msg_ids()
    with safe_open(f"{DATADIR}/last_message.txt", "r") as content:
        try:
            if not TELEGRAM_EDIT: # Send a New Message
                LOGGER.info('Sending Message to Telegram Channel...')
                last_message = await bot.send_message(
                    text = message.markdown,
                    chat_id = channel_id,
                    parse_mode="MarkdownV2",
                    disable_web_page_preview=True)
                last_msg_ids[TELEGRAM_CHANNEL] = last_message.message_id
                with safe_open(f"{DATADIR}/message_ids.yml", "w") as ids:
                    yaml.dump(last_msg_ids, ids, yaml.Dumper)
                content.seek(0), content.write(message.txt), content.truncate() # write message content to file to be able to check if it has changed
                LOGGER.info(f"Successfully sent message to Telegram Channel {TELEGRAM_CHANNEL}!")
            else: # Edit the last Message
                LOGGER.info('Editing last Message in Telegram Channel...')
                if content.read() == message.txt:
                    LOGGER.info("Message has not changed since the last edit. No changes applied.")
                else:
                    await bot.edit_message_text(text=message.markdown,
                        message_id=last_msg_ids[TELEGRAM_CHANNEL],
                        chat_id=channel_id,
                        parse_mode="MarkdownV2",
                        disable_web_page_preview=True)
                    content.seek(0), content.write(message.txt), content.truncate()
                    LOGGER.info(f"Successfully edited last message in Telegram Channel: {channel_id}!")
        except BadRequest: # if something goes wrong
            LOGGER.exception(f"Something went wrong while working in telegram channel: {TELEGRAM_CHANNEL} - Aborting, please try again.\n")
            LOGGER.debug(message)
    return

 