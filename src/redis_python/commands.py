from .store import Store

from .protocols.values import RESP, Array, BulkString, Integer, SimpleError, SimpleString


class CommandHandler:
    def __init__(self, store: Store) -> None:
        self.store = store

    def handle(self, command: Array) -> RESP:
        original_name = command.data[0].data.decode(errors="replace")
        name = command.data[0].data.upper()
        if name == b"GET":
            if command.length != 2:
                return self._wrong_args("get")
            else:
                return BulkString(self.store.get(command.data[1].data))

        elif name == b"SET":
            if command.length != 3:
                return self._wrong_args("set")
            else:
                self.store.set(command.data[1].data, command.data[2].data)
                return SimpleString("OK")

        elif name == b"DEL":
            if command.length < 2:
                return self._wrong_args("del")
            else:
                count = 0
                for item in command.data[1:]:
                    count += 1 if self.store.delete(item.data) else 0
                return Integer(count)
        elif name == b"EXISTS":
            if command.length < 2:
                return self._wrong_args("exists")
            else:
                count = 0
                for item in command.data[1:]:
                    count += 1 if self.store.exists(item.data) else 0
                return Integer(count)

        elif name == b"PING":
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
    def _wrong_args(self, name: str) -> SimpleError:
        return SimpleError(f"ERR wrong number of arguments for '{name}' command")