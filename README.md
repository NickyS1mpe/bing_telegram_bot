# Bing Telegram Auto Reply Bot

A Telegram auto-reply bot using the gpt4free Bing api implemented in Python

## Overview

This is a Telegram auto-reply bot implemented in Python using the gpt4free Bing API. It replies to messages and images
in
Telegram chats based on predefined prompts. The bot utilizes gpt4free Bing API to generate responses, making it capable
of engaging in conversations with users both in group and private chats.

## Features

- Automatically replies to messages in Telegram group and private chats.
- Utilizes the gpt4free Bing API for response generation.
- Supports interaction with both text and photos.
- Supports chat history caching.
- Can be customized with specific prompts for different AI personalities and behaviors.
- Logs interactions of user and AI for monitoring and analysis.

## Environment

- Python 3.11+ with pip.
- Windows 10+, Linux or macOS.

## Configuration

1. Replace the `bot_token` with your own Telegram bot token.
2. Customize the `prompt` variable to define the personality and behavior of the AI.
3. Replace the values of `bot_nickname`, `bot_username`, and `group_user_nickname` as needed to match your Telegram
   bot and groups.
4. Create a new folder named "image" to cache images.

## How to use

1. Installed required dependencies using pip(g4f, etc).
2. Create your own Telegram bot and obtain a unique token from [@BotFather](https://core.telegram.org/bots)
3. Add your bot to your desired group where you want the bot to run (admin privileges required), and add the group
   name and enable status (default to True) in the 'group' dictionary.
4. Put your cookies.json in the same folder as the executable file(if needed). Currently, my code utilizes the GPT-4
   model provided by Bing, which requires the use of cookies. You can refer to
   the [SydneyQT](https://github.com/juzeon/SydneyQt) for specific instructions on
   how to obtain the cookie file, or chat with Sydney locally by yourself.
5. Run the program.

## Bot commands

- `/info`: Get basic information about the bot.
- `/enable_bot`: Enable the bot to start responding to messages.
- `/disable_bot`: Disable the bot to stop responding to messages.
- You can add any desired commends through @BotFather and implement them using the Telegram APIs.

## Screenshots

![IMG_0419](https://github.com/NickyS1mpe/Bing-Telegram-Bot/assets/71556158/0484703d-135c-458e-a86c-a660d1abd2e7)
![IMG_0420](https://github.com/NickyS1mpe/Bing-Telegram-Bot/assets/71556158/f2998ad3-10c3-43dd-9cbe-dc324033d703)


## Incoming updates

1. Image generation.

## API usage & Credit

- You can modify the reply functionality based on various parameters provided by the gpt4free API, such as models,
  providers and
  proxies.
- Reference: [gpt4free](https://github.com/xtekky/gpt4free)
