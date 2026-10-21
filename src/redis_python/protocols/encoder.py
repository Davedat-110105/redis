"""Encode supported RESP2 values as wire bytes."""

from .types import BulkStrings, Integers, RESPValue, SimpleError, SimpleString


class Encoder:
    """Serialize a RESP2 value without performing network I/O."""

    def __init__(self, data: RESPValue) -> None:
        self.data = data

    def convert(self) -> bytes:
        """Return wire bytes, raising TypeError for unsupported values."""
        match self.data:
            case SimpleString(data=text) | SimpleError(data=text):
                payload = text.encode("utf-8")
            case Integers(data=number):
                payload = str(number).encode("ascii")
            case BulkStrings(data=content):
                if content is None:
                    payload = b"-1"
                else:
                    length = str(self.data.length).encode("ascii")
                    payload = length + self.data.final_terminator + content
            case _:
                raise TypeError("Unsupported RESP value")

        return self.data.prefix + payload + self.data.final_terminator
