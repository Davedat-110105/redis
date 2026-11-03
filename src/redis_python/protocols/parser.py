"""Parse supported RESP2 values using a byte reader."""

from .byte_reader import ByteReader
from .values import Array, BulkString, Integer, RESPValue, SimpleError, SimpleString


class RESPParser:
    """Interpret RESP2 values while ByteReader manages the input position."""

    def __init__(self, data: bytes) -> None:
        self.reader = ByteReader(data)

    @property
    def data(self) -> bytes:
        """Return the input bytes held by the reader."""
        return self.reader.data

    @property
    def cursor(self) -> int:
        """Expose the reader's position so the server can retain unread bytes."""
        return self.reader.cursor

    def parse(self) -> RESPValue:
        """Parse one value, restoring its starting position on failure.

        The checkpoint covers the whole value, including nested array items.

        Raises:
            EOFError: If the buffer ends before the value is complete.
            ValueError: If the wire format is invalid or unsupported.
        """
        start = self.reader.mark()
        try:
            return self._parse_value()
        except (EOFError, ValueError):
            self.reader.reset(start)
            raise

    def _parse_value(self) -> RESPValue:
        """Consume a type prefix and choose the parser for its contents."""
        prefix = self.reader.read_exact(1)
        if prefix == b"+":
            return self._parse_simple_string()
        if prefix == b"-":
            return self._parse_error()
        if prefix == b":":
            return self._parse_integer_value()
        if prefix == b"$":
            return self._parse_bulk_string()
        if prefix == b"*":
            return self._parse_array()
        raise ValueError(f"Unsupported RESP2 prefix: {prefix!r}")

    def _parse_simple_string(self) -> SimpleString:
        return SimpleString(self._read_text_line())

    def _parse_error(self) -> SimpleError:
        return SimpleError(self._read_text_line())

    def _parse_integer_value(self) -> Integer:
        return Integer(self._parse_integer(self.reader.read_line()))

    def _parse_bulk_string(self) -> BulkString:
        length = self._parse_integer(self.reader.read_line())
        if length == -1:
            return BulkString(None)
        if length < -1:
            raise ValueError("Invalid RESP2 bulk string length")

        payload = self.reader.read_exact(length)
        if self.reader.read_exact(2) != b"\r\n":
            raise ValueError("Missing RESP2 bulk string terminator")
        return BulkString(payload)

    def _parse_array(self) -> Array:
        length = self._parse_integer(self.reader.read_line())
        if length == -1:
            return Array(None)
        if length < -1:
            raise ValueError("Invalid RESP2 array length")

        items = [self._parse_value() for _ in range(length)]
        return Array(items)

    def _read_text_line(self) -> str:
        try:
            return self.reader.read_line().decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Invalid UTF-8 in RESP2 text") from exc

    @staticmethod
    def _parse_integer(value: bytes) -> int:
        """Convert a RESP integer or length header into a Python integer."""
        digits = value[1:] if value.startswith(b"-") else value
        if not digits or not digits.isdigit():
            raise ValueError("Invalid RESP2 integer")
        return int(value)
