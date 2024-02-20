import os
import sys
import random
import time
import asyncio
import requests
import json
import logging
import re
import g4f
from datetime import datetime, timedelta

# Bot token from Telegram BotFather
bot_token = ''
api = f'https://api.telegram.org/bot{bot_token}/'

# Use your own prompt to define the personality and behavior of the AI
bot_responsibility = '''
prompt
'''
# Bot statement
bot_statement = f"*statement*"
# Bot nickname
bot_nickname = r'[nickname]'
# Bot username
bot_username = '@username'
group_user_nickname = ""
# Allowed group and the enable status of the group
group = {
    'private': True
}
block_user = []
# Cookies if needed
cookies_dict = {}
# Randomly reply rate
comment_rate = 0.005
# Chat history
history_message = []
# Maximum history quantity
history_number = 10
# Maximum length of the reply from AI
max_len = 200

# log
log_file = 'bot.log'
logging.basicConfig(filename=log_file,
                    level=logging.INFO)


# Logging
def log_message(update):
    user_name = update['message']['from_user']['user_name']
    chat_name = update['chat']['chat_name']
    is_bot = update['message']['from_user']['is_bot']
    message_type = update['message']['message_type']
    message_content = update['message']['text']

    logging.info(
        '%(asctime)s - %(user_name)s - %(chat_name)s - %(is_bot)s - %(message_type)s - %(message_content)s',
        {'asctime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'user_name': user_name,
         'chat_name': chat_name, 'is_bot': is_bot,
         'message_type': message_type,
         'message_content': message_content})


def build_submission_context(name, context, group_name):
    context_str = f'[system](#context)\nHere is the comment made by {group_user_nickname} : {name} in a group named {group_name}\n'
    # Limit the length of content
    if context != "":
        context_str += f", the content is “{context[:3000]}”"
    context_str += "\n\n"
    context_str += f"[system][#additional_instructions]\nWhen replying, instead of repeating or imitating what the {name} you are replying to said, you reply with your own creativity. Needn't introduce yourself. Only output the body of your reply. Do not attach the original text, do not output all possible replies."
    return context_str


def remove_extra_format(reply: str) -> str:
    pattern = r'reply[^：]*：(.*)'
    result = re.search(pattern, reply, re.S)
    if result is None:
        return reply
    result = result.group(1).strip()
    if result.startswith("“") and result.endswith("”"):
        result = result[1:-1]
    return result


# Fetch the information of bot
def getMe():
    return json.loads(requests.get(api + 'getMe').content)


# Reply to message via bot
def telegram_bot_sendText(bot_msg, chat_id, msg_id):
    data = {
        'chat_id': chat_id,
        'text': bot_msg,
        'reply_to_message_id': msg_id
    }
    url = api + 'sendMessage'

    response = requests.post(url, data=data)
    return response.json()


# Send text via bot
def telegram_bot_send(bot_msg, chat_id):
    data = {
        'chat_id': chat_id,
        'text': bot_msg,
    }
    url = api + 'sendMessage'

    response = requests.post(url, data=data)
    return response.json()


# Send photo via bot
def telegram_bot_sendImage(image_url, chat_id, msg_id):
    data = {
        'chat_id': chat_id,
        'photo': image_url,
        'reply_to_message_id': msg_id
    }
    url = api + 'sendPhoto'

    response = requests.post(url, data=data)
    return response.json()


# Fetch photo via bot
def telegram_bot_getImage(file_id, update_id):
    # Fetch the location of the photo in Telegram server
    location = api + 'getFile?file_id=' + file_id
    response = requests.get(location)
    response_dict = response.json()
    file_path = response_dict['result']['file_path']
    # Download the image
    image_url = 'https://api.telegram.org/file/bot' + bot_token + '/' + file_path
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(f'image/{update_id}.jpg', 'wb') as f:
            f.write(response.content)
    return image_url


# insert message into chat history
def insert_message(context):
    history_message.append(context)
    # If the history exceeds the specified quantity then pop it out
    if len(history_message) > history_number:
        history_message.pop()


async def reply(context, chat_id, msg_id, update, image_url):
    # Insert the current message into chat history and send them to AI
    cur_msg = {'role': 'user', 'content': context}
    ask = {'role': 'system', 'content': "Please reply to the conversation."}
    insert_message(cur_msg)
    history_message.append(ask)
    try:
        response = await g4f.ChatCompletion.create_async(
            # Current model
            model=g4f.models.gpt_4,
            messages=history_message,
            web_search=True,
            # cookies
            cookies=cookies_dict,
            # Current service provider
            provider=g4f.Provider.Bing,
            image=open(image_url, "rb") if image_url != "" else ""
        )
        context_reply = remove_extra_format(response)
        reply_msg = {'role': 'assistant', 'content': context_reply}
        history_message.pop()
        insert_message(reply_msg)
        # Renew the log content
        update['message']['text'] = context_reply
        log_message(update)
        # Reply to message
        telegram_bot_sendText(context_reply[:max_len] + bot_statement, chat_id, msg_id)
        # Delete the local photo cache
        if os.path.exists(image_url):
            os.remove(image_url)
        return context_reply

    except Exception as e:
        logging.error(e)


def task():
    # Fetch the current document location
    cwd = os.getcwd()
    # Get the timestamp in timer_log.txt or create a new one if it isn't existed
    timer_log = cwd + '/timer_log.txt'
    if not os.path.exists(timer_log):
        with open(timer_log, "w") as f:
            f.write('1')
    # else:
    # print("Timer Log Exists")

    with open(timer_log) as f:
        last_update = f.read()

    # Set offset based on timestamp to fetch the latest messages
    url = f'{api}getUpdates?offset={last_update}'
    response = requests.get(url)
    data = json.loads(response.content)
    global bot_enable

    # Read the data
    for res in data['result']:
        try:
            if 'message' in res:
                image_url = ''
                comment = ''
                update_id = res['update_id']
                # If data type is photo
                if 'photo' in res['message'] and 'caption' in res['message']:
                    comment = res['message']['caption']
                    file_id = res['message']['photo'][len(res['message']['photo']) - 1]['file_id']
                    image_url = telegram_bot_getImage(file_id, update_id)
                # If data type is text
                elif 'text' in res['message']:
                    comment = res['message']['text']

                if float(update_id) > float(last_update) and comment != "":
                    if not res['message']['from']['is_bot']:
                        global history_message
                        msg_id = res['message']['message_id']
                        chat_id = res['message']['chat']['id']
                        group_name = res['message']['chat']['title'] if 'title' in res['message']['chat'] else \
                            res['message']['chat']['type']
                        user_name = res['message']['from']['first_name']
                        message_type = res['message']['chat']['type']

                        # Check is the bot is allowed to use in the group, and the bot is enabled
                        if group_name in group:
                            if group[group_name]:

                                # Build the content that is going to send to AI
                                context = bot_responsibility
                                context += build_submission_context(
                                    user_name, comment, group_name)

                                # Set the log contents
                                update = {'message': {'from_user': {'user_name': user_name, 'is_bot': 'False'},
                                                      'message_type': message_type,
                                                      'text': comment.replace("\n", "").replace("\t", "")},
                                          'chat': {'chat_name': group_name}}

                                reply_update = {
                                    'message': {'from_user': {'user_name': bot_nickname, 'is_bot': 'True'},
                                                'message_type': message_type,
                                                'text': ""},
                                    'chat': {'chat_name': group_name}}

                                # Disable the bot in a group
                                if '/disable_bot' in comment:
                                    group[group_name] = False
                                    update['message']['message_type'] = 'command'
                                    log_message(update)
                                    print(telegram_bot_send('Bot disabled', chat_id))
                                # Return the introduction of the bot
                                elif '/info' in comment:
                                    bot_info = getMe()
                                    bot_response = "I'm a Telegram auto reply BOT - " + f"{bot_info['result']['first_name']}"
                                    update['message']['message_type'] = 'command'
                                    log_message(update)
                                    print(telegram_bot_send(bot_response + bot_statement, chat_id))
                                # Clear chat history
                                elif '/clear_history' in comment:
                                    history_message = []
                                    update['message']['message_type'] = 'command'
                                    log_message(update)
                                    print(telegram_bot_send('History cleared', chat_id))
                                # If the bot is mentioned in the comment or the bot can randomly reply
                                elif (re.search(bot_nickname, comment) is not None
                                      or f'{bot_username}' in comment or random.random() < comment_rate):
                                    log_message(update)
                                    asyncio.run(
                                        reply(context, chat_id, msg_id, reply_update, image_url))
                                # If the message of bot is replied
                                elif 'reply_to_message' in res['message'] and \
                                        res['message']['reply_to_message']['from']['is_bot']:
                                    log_message(update)
                                    asyncio.run(
                                        reply(context, chat_id, msg_id, reply_update, image_url))

                            # Enable the bot in a group
                            if '/enable_bot' in comment:
                                group[group_name] = True
                                print(telegram_bot_send('Bot enabled', chat_id))

                # Renew the timestamp
                with open(timer_log, "w") as f:
                    f.write(f'{update_id}')

        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    # Loading cookies
    with open("./cookies.json", encoding="utf-8") as f:
        cookies_data = json.load(f)
    cookies_dict = {index: dictionary for index, dictionary in enumerate(cookies_data)}

    # Enable debug logging
    g4f.debug.logging = True
    # Disable automatic version checking
    g4f.debug.version_check = False
    # Print supported args for Bing
    print(g4f.Provider.Bing.params)
    # Print the basic information of bot
    print(getMe())
    # Set random seed
    random.seed()
    # Get the current timestamp
    timestamp1 = datetime.now()

    while True:
        try:
            task()
        except BaseException as e:
            logging.error(e)
            sys.exit()

        # Clear the chat history if the current time internal greater than the setting interval
        timestamp2 = datetime.now()
        if timestamp2 - timestamp1 > timedelta(minutes=3):
            timestamp1 = timestamp2
            history_message = []

        time.sleep(10)
