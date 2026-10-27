from .store import Store

from .protocols.values import RESP, Array, BulkString, SimpleError, SimpleString


class CommandHandler:
    def __init__(self, store: Store) -> None:
        self.store = store

    def handle(self, command: Array) -> RESP:
        original_name = command.data[0].data.decode()
        name = command.data[0].data.upper()
        if name == b"PING":
            if command.length < 2:
                return SimpleString("PONG")
            else:
                return BulkString(command.data[1].data)
        elif name == b"ECHO":
            if command.length != 2:
                return SimpleError("ERR wrong number of arguments for 'echo' command")
            else:
                return BulkString(command.data[1].data)
        else:
            return SimpleError(f"ERR unknown command '{original_name}'")