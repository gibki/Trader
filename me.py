import config

from telethon import TelegramClient

client = TelegramClient('Trader', config.API_ID, config.API_HASH)

async def main():
    # Getting information about yourself
    me = await client.get_me()
    print(me)

with client:
    client.loop.run_until_complete(main())