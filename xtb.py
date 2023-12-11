import config

import socket, json, ssl, time


class CMD:
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP =	5
    BALANCE = 6  # Read only. Used in getTradesHistory for manager's deposit/withdrawal operations (profit>0 for deposit, profit<0 for withdrawal).
    CREDIT = 7	# Read only

class TYPE:
    OPEN = 0	# order open, used for opening orders
    PENDING = 1	# order pending, only used in the streaming getTrades command
    CLOSE = 2	# order close
    MODIFY = 3	# order modify, only used in the tradeTransaction command
    DELETE = 4	# order delete, only used in the tradeTransaction command

class STATUS:
    ERROR = 0
    PENDING = 1
    ACCEPTED = 3
    REJECTED = 4

class XTBClient:
    def __init__(self, user_id=config.USER_ID, user_password=config.USER_PASSWORD):
        self.ssl_context = ssl.create_default_context()
        self.user_id = user_id
        self.user_password = user_password

    def __enter__(self):
        self.plain_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM).__enter__()
        self.socket = self.ssl_context.wrap_socket(self.plain_socket, server_hostname=config.HOST).__enter__()
        self.socket.connect((config.HOST, config.PORT))
        login_response = self.login(self.user_id, self.user_password)
        assert login_response['status'] == True
        return self

    def __exit__(self, type, value, traceback):
        self.socket.__exit__(type, value, traceback)
        return self.plain_socket.__exit__(type, value, traceback)

    def _send_command(self, command, arguments):
        data = {
            "command": command,
            "arguments": arguments,
        }
        print(data)
        json_data = json.dumps(data)
        binary_data = json_data.encode("utf-8")

        self.socket.sendall(binary_data)
        response = b''
        while True:
            response += self.socket.recv(1024)
            try:
                return json.loads(response.decode("utf-8"))
            except json.JSONDecodeError:
                pass

    def login(self, user_id, password, app_name=None, app_id=None):
        arguments = {
                "userId": user_id,
                "password": password,
            }
        if app_name is not None:
            arguments["appId"] = app_name
        if app_id is not None:
            arguments["appId"] = app_id

        return self._send_command("login", arguments)

    def transaction(self, cmd, type, symbol, price, take_profit, stop_loss, volume, order=0):
        arguments = {
            "cmd": cmd,
            "type": type,

            "customComment": symbol,
            # "expiration": 1462006335000,
            # "offset": 0,

            "order": order,
            "symbol": symbol,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "volume": volume,
        }
        create_response = self._send_command("tradeTransaction", {"tradeTransInfo": arguments})
        if create_response['status']:
            order = create_response['returnData']['order']
            status = STATUS.PENDING
            count = 0
            while status == STATUS.PENDING and count < 100:
                transaction_status = self._send_command("tradeTransactionStatus", {"order": order})
                if not transaction_status['status'] or transaction_status['returnData']['requestStatus'] != STATUS.PENDING:
                    return transaction_status
                print("pending...")
                time.sleep(0.2)
                count += 1

        return create_response

    def create_new(self, symbol, command, price, tp, sl, volume):
        return self.transaction(command, TYPE.OPEN, symbol, price, tp, sl, volume)
    
    def get_trades(self):
        return self._send_command("getTrades", {
		    "openedOnly": True
	    })
    
    
    def modify(self, cmd, order, symbol, price, tp, sl, volume):
        # return self.transaction(cmd, TYPE.MODIFY, symbol, price, tp, sl, volume, order)
        return self.transaction(cmd, TYPE.OPEN, symbol, price, tp, sl, volume, order)

    # def promote(socket, order):
    #     transaction_status = send_command(socket, "tradeTransactionStatus", {"order": order})
    #     print(transaction_status)
    #     price_before = transaction_status['returnData']['ask']
    #     price = round(price_before + 0.2, 2)
    #     symbol = transaction_status['returnData']['customComment']
    #     transaction(socket, CMD.BUY_STOP, TYPE.DELETE, symbol, 0.0, 0.0, 0.0, 0.0, order)
    #     return transaction(socket, CMD.BUY_STOP, TYPE.OPEN, symbol, round(price, 4), round(price, 4), round(price + 0.5, 4), 0.01)

# with XTBClient() as c:
#     result = c.modify(CMD.BUY, 577899187, "USDCAD", 1.3204, 1.3204, 1.3254, 0.02)
#     print(result)
