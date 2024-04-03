import logging
from bewegungskalender.server.auto_git import get_git_remote, init_git_repo
from git import Remote, Repo
import telegram
import yaml
from telegram.constants import ParseMode
from telegram import Bot

def bot(config:dict) -> Bot:
    """
    get a Telegram Bot object with token from config
    """
    bot:telegram.Bot = Bot(token=config['telegram']['token'])
    return bot

async def get_telegram_updates(config:dict):
    """
    telegram helper method to retrieve group_ids of groups that the bot joined
    """
    logging.debug('Getting telegram updates...')
    updates = await bot(config).get_updates()
    return "\n".join([str(u) for u in updates])

async def send_telegram(args:dict, config:dict, repo:Repo, origin:Remote, message:str) -> None:
    if len(message) > 8000: # Check if message is too long for telegram
        logging.exception(f"Could not send message with {len(message)} characters to telegram, message longer than 8000 characters. Aborting."); exit(1)
    
    try:
        if args.telegram == 'prod': #  Handle --telegram argument and send to production if specified
            lastmessage:dict = await bot(config).send_message(text=message, 
                                                            chat_id=config['telegram']['production'], 
                                                            parse_mode=ParseMode.MARKDOWN_V2, 
                                                            disable_web_page_preview=True)      
        else: # send message to testchannel
            lastmessage:dict = await bot(config).send_message(text=message, 
                                                            chat_id=config['telegram']['test'], 
                                                            parse_mode=ParseMode.MARKDOWN_V2, 
                                                            disable_web_page_preview=True)
    except telegram.error.TelegramError: # if something goes wrong
        logging.exception(f"Something went wrong while sending message to telegram channel: {args.telegram} - Aborting, please try again.\n")
        logging.debug(f"{message}")
    with open(f"{repo.working_dir}/message_ids.yml", "w") as f: 
        f.write(f"{args.telegram}: {lastmessage.message_id}") # write message_id of the message sent to file to be able to edit it
        repo.index.add('message_ids.yml'); repo.index.commit("Updated message_ids.yml"); origin.push('main') # git stage, commit and push
        logging.info(f"Pushed {repo.working_dir}/message_ids.yml to {origin.url}!")
    return

async def edit_telegram(args:dict, config:dict, origin:Remote, message:str) -> None:
    if len(message) > 8000: # Check if message is too long for telegram
        logging.exception(f"Could not send message with {len(message)} characters to telegram, message longer than 8000 characters. Aborting."); exit(1)
    try: # Get ID of last Message sent
        origin.pull('main')
        with open(f"{config['data']['localdir']}/message_ids.yml", "r") as f: 
            message_ids:dict = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logging.exception(f"{config['data']['localdir']}/message_ids.yml: File with message_ids not Found"); exit()
    
    try: # Edit last message sent
        if args.edit_telegram == 'prod': #  Handle cli argument and edit message in channel prod if specified
            await bot(config).edit_message_text(text=message, 
                                                message_id=message_ids['prod'], 
                                                chat_id=config['telegram']['production'], 
                                                parse_mode=ParseMode.MARKDOWN_V2, 
                                                disable_web_page_preview=True)     
        else: # otherwise edit message in testchannel
            await bot(config).edit_message_text(text=message, 
                                                message_id=message_ids['test'], 
                                                chat_id=config['telegram']['test'], 
                                                parse_mode=ParseMode.MARKDOWN_V2, 
                                                disable_web_page_preview=True)
        logging.info(f"Succesfully edited last message in Telegram Channel: {args.edit_telegram}!")
    except telegram.error.BadRequest: # if message has not changed throw an exception
        logging.error(f"Telegram message was not modified. Seems like there have been no changes. \n")
        print(message)
    return
    
     
 