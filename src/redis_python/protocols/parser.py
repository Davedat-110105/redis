from typing import Optional

from .types import SimpleString, Integers, BulkStrings

class Decoder():
    def __init__(self, data: bytes):
        self.data = data
        self.cursor = 0


    def parsing(self) -> Optional[SimpleString | Integers | BulkStrings]:
        if (self.data.startswith(b"+")):
            end = self.data.find(b"\r\n", 1)
            payload = self.data[1:end]
            text = payload.decode("utf-8")
            return SimpleString(text)
        if (self.data.startswith(b":")):
            end = self.data.find(b"\r\n", 1)
            payload = self.data[1:end]
            number = int(payload.decode("utf-8"))
            return Integers(number)
        if (self.data.startswith(b"$")):
            end_length = self.data.find(b"\r\n", 1)
            payload_length = int((self.data[1:end_length]).decode("utf-8"))
            if payload_length == -1:
                return BulkStrings(None)
            start = end_length + 2
            end = start + payload_length
            payload = self.data[start:end]
            return BulkStrings(payload)
