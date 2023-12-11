import config

import re, json

from telethon import TelegramClient, events
from xtb import XTBClient, CMD

client = TelegramClient('Trader', config.API_ID, config.API_HASH)

# example message
# CHFJPY BUY @ 164.83 / 164.88

#             TP: 165.03 (scalper) 
#             TP: 165.33 (intraday) 
#             TP: 165.83 (swing)
#             SL: 164.23

#             🟢 Uzywaj MM  2-3%
#          symbol     command              price
#          --------   --------------       -----------
# PATTERN = r"\s*([A-Z]+)\s+"
# PATTERN = r"\s*([A-Z]+)\s+((BUY)|(SELL))\s*@\s*(\d+\.\d+)(\s*/\s*(\d+\.\d+))?\s*TP:"
PATTERN1 = r"\s*([A-Z0-9]+)\s+((BUY)|(SELL)|(buy)|(sell))\s*@\s*(\d+\.\d+)(\s*/\s*(\d+\.\d+))?\s*TP:\s*(\d+\.\d+).*\n\s*TP:\s*(\d+\.\d+).*\n\s*TP:\s*(\d+\.\d+).*\n\s*SL:\s*(\d+\.\d+)"
MATCHER1 = re.compile(PATTERN1)

PATTERN2 = r"\s*([A-Z0-9]+)\s+((BUY)|(SELL)|(buy)|(sell)).*\n\s*ENTRY\s+\@\s+(\d+.\d+)\s*\n\s*SL:\s+(\d+.\d+).*\n\s*TP1:\s+(\d+.\d+).*\n\s*TP2:\s+(\d+.\d+).*\n\s*TP3:\s+(\d+.\d+)"
MATCHER2 = re.compile(PATTERN2)

PATTERN3 = r"\s*([A-Z0-9]+)\s+((BUY)|(SELL)|(buy)|(sell))\s+(\d+).*\n\s*SL\s+(\d+).*\n\s*TP\s+(\d+).*\n\s*TP\s+(\d+).*\n\s*TP\s+(\d+).*\n\s*TP\s+(\d+)"
MATCHER3 = re.compile(PATTERN3)

ORDERS = {}

def parse_message(text):
    # type 1
    result = MATCHER1.match(text)
    if result is not None:
        symbol = result.group(1)
        command = result.group(2)
        price = float(result.group(7))
        tp1 = float(result.group(10))
        tp2 = float(result.group(11))
        tp3 = float(result.group(12))
        sl = float(result.group(13))
        print("Symbol:", symbol, "command:", command, "price:", price)
        if command == "BUY" or command == 'buy':
            command = CMD.BUY
        if command == "SELL" or command == 'sell':
            command = CMD.SELL
        return {
            "symbol": symbol,
            "command": command,
            "price": price,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "sl": sl,
        }
    result = MATCHER2.match(text)
    if result is not None:
        # print(result.groups())
        symbol = result.group(1)
        command = result.group(2)
        if command == "BUY" or command == 'buy':
            command = CMD.BUY
        if command == "SELL" or command == 'sell':
            command = CMD.SELL
        price = float(result.group(7))
        sl = float(result.group(8))
        tp1 = float(result.group(9))
        tp2 = float(result.group(10))
        tp3 = float(result.group(11))
        return {
            "symbol": symbol,
            "command": command,
            "price": price,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "sl": sl,
        }
    result = MATCHER3.match(text)
    if result is not None:
        print(result.groups())
        symbol = result.group(1)
        command = result.group(2)
        if command == "BUY" or command == 'buy':
            command = CMD.BUY
        if command == "SELL" or command == 'sell':
            command = CMD.SELL
        price = float(result.group(7))
        sl = float(result.group(8))
        tp1 = float(result.group(9))
        tp2 = float(result.group(10))
        tp3 = float(result.group(11))
        return {
            "symbol": symbol,
            "command": command,
            "price": price,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "sl": sl,
        }
    return None

@client.on(events.NewMessage(from_users=config.CHANNEL_ID))
async def handler(event):
    print("New message:", event.message.text)
    parsed_message = parse_message(event.message.text)
    if parsed_message is not None:
        orders = []
        with XTBClient() as xtb_client:
            for tp, volume in [(parsed_message['tp1'], 0.03), (parsed_message['tp2'], 0.02), (parsed_message['tp3'], 0.01)]:
                response = xtb_client.create_new(parsed_message['symbol'], parsed_message['command'], parsed_message['price'], tp, parsed_message['sl'], volume)
                print(response)
        if len(orders) > 0:
            ORDERS[event.message.id] = orders
            
    else:
        if event.message.reply_to is not None and event.message.reply_to.reply_to_msg_id in ORDERS:
            if event.message.text.startswith("TP"):
                record = ORDERS[event.message.reply_to.reply_to_msg_id]
                # with XTBClient() as xtb_client:
                #     for order in record:
                #         result = xtb_client.modify(order['cmd'], order['order'], order['symbol'], order['price'], order['tp'], order['price'], order['volume'])
                #         print(result)
        else:
            print("Not a command")

if __name__ == '__main__':
    try:
        with open("orders.json", "r") as f:
            ORDERS = json.loads(f.read())
    except FileNotFoundError:
        print("No order database found, starting a new one")
    except json.JSONDecodeError:
        print("Order database corrupted, exiting")
        exit(1)
    try:
        client.start()
        client.run_until_disconnected()
    finally:
        with open("orders.json", "w") as f:
            f.write(json.dumps(ORDERS))
