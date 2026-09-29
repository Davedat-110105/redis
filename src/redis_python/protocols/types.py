"""Value objects for the supported RESP2 protocol types."""

from typing import ClassVar


class RESP:
    """Base for RESP2 values sharing a CRLF terminator."""

    final_terminator: ClassVar[bytes] = b"\r\n"


class SimpleString(RESP):
    """Hold a simple string, whose content must not contain CR or LF."""

    prefix: ClassVar[bytes] = b"+"

    def __init__(self, data: str) -> None:
        self._validate(data)
        self.data = data

    @staticmethod
    def _validate(data: str) -> None:
        if "\r" in data or "\n" in data:
            raise ValueError("SimpleString cannot contain CR or LF")


class SimpleError(RESP):
    """Hold an error reply as text rather than a Python exception."""

    prefix: ClassVar[bytes] = b"-"

    def __init__(self, data: str) -> None:
        self._validate(data)
        self.data = data

    @staticmethod
    def _validate(data: str) -> None:
        if "\r" in data or "\n" in data:
            raise ValueError("SimpleError cannot contain CR or LF")

class Integers(RESP):
    """Hold a signed integer reply, excluding Python booleans."""

    prefix: ClassVar[bytes] = b":"

    def __init__(self, data: int) -> None:
        if isinstance(data, bool) or not isinstance(data, int):
            raise TypeError("data must be an integer")
        self.data = data


class BulkStrings(RESP):
    """Hold raw bytes, or None for a null bulk string."""

    prefix: ClassVar[bytes] = b"$"

    def __init__(self, data: bytes | None) -> None:
        self.data = data

    @property
    def length(self) -> int:
        """Return the byte length of the payload, or -1 when null."""
        return -1 if self.data is None else len(self.data)
