"""Value objects for the supported RESP2 protocol types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar


class RESP(ABC):
    """Base for RESP2 values sharing a CRLF terminator."""

    prefix: ClassVar[bytes]
    final_terminator: ClassVar[bytes] = b"\r\n"

    @abstractmethod
    def encode(self) -> bytes:
        """Return the RESP2 wire bytes for this value."""


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

    def encode(self) -> bytes:
        return self.prefix + self.data.encode("utf-8") + self.final_terminator


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

    def encode(self) -> bytes:
        return self.prefix + self.data.encode("utf-8") + self.final_terminator


class Integer(RESP):
    """Hold a signed integer reply, excluding Python booleans."""

    prefix: ClassVar[bytes] = b":"

    def __init__(self, data: int) -> None:
        if isinstance(data, bool) or not isinstance(data, int):
            raise TypeError("data must be an integer")
        self.data = data

    def encode(self) -> bytes:
        return self.prefix + str(self.data).encode("ascii") + self.final_terminator


class BulkString(RESP):
    """Hold raw bytes, or None for a null bulk string."""

    prefix: ClassVar[bytes] = b"$"

    def __init__(self, data: bytes | None) -> None:
        self.data = data

    @property
    def length(self) -> int:
        """Return the byte length of the payload, or -1 when null."""
        return -1 if self.data is None else len(self.data)

    def encode(self) -> bytes:
        if self.data is None:
            return self.prefix + b"-1" + self.final_terminator

        length = str(self.length).encode("ascii")
        payload = length + self.final_terminator + self.data
        return self.prefix + payload + self.final_terminator


class Array(RESP):
    """Hold a list of RESP values, or None for a null array."""

    prefix: ClassVar[bytes] = b"*"

    def __init__(self, data: list[RESPValue] | None) -> None:
        self.data = data

    @property
    def length(self) -> int:
        """Return the number of items, or -1 when null."""
        return -1 if self.data is None else len(self.data)

    def encode(self) -> bytes:
        header = self.prefix + str(self.length).encode("ascii") + self.final_terminator
        if self.data is None:
            return header
        result = header
        for item in self.data:
            result += item.encode()
        return result


RESPValue = SimpleString | SimpleError | Integer | BulkString | Array
