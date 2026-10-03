"""Decode supported RESP2 values from a byte buffer."""

from .types import BulkStrings, Integers, SimpleError, SimpleString

RESPValue = SimpleString | SimpleError | Integers | BulkStrings


class Decoder:
    """Read consecutive RESP2 values from a byte buffer."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.cursor = 0

    def _read_line(self, start: int) -> tuple[bytes, int]:
        end = self.data.find(b"\r\n", start)
        if end == -1:
            raise EOFError("Incomplete RESP2 line")
        line = self.data[start:end]
        if b"\r" in line or b"\n" in line:
            raise ValueError("Invalid line ending in RESP2 header")
        return line, end + 2

    @staticmethod
    def _parse_integer(value: bytes) -> int:
        digits = value[1:] if value.startswith(b"-") else value
        if not digits or not digits.isdigit():
            raise ValueError("Invalid RESP2 integer")
        return int(value)

    def parsing(self) -> RESPValue:
        """Decode the next value and advance the cursor on success.

        Raises:
            EOFError: If the buffer ends before the value is complete.
            ValueError: If the wire format is invalid or unsupported.
        """
        if self.cursor >= len(self.data):
            raise EOFError("No RESP2 value available")

        prefix = self.data[self.cursor : self.cursor + 1]
        if prefix in (b"+", b"-", b":"):
            line, next_cursor = self._read_line(self.cursor + 1)
            if prefix == b":":
                value: RESPValue = Integers(self._parse_integer(line))
            else:
                try:
                    text = line.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise ValueError("Invalid UTF-8 in RESP2 text") from exc
                value = SimpleString(text) if prefix == b"+" else SimpleError(text)
        elif prefix == b"$":
            line, next_cursor = self._read_line(self.cursor + 1)
            length = self._parse_integer(line)
            if length == -1:
                value = BulkStrings(None)
            elif length < -1:
                raise ValueError("Invalid RESP2 bulk string length")
            else:
                end = next_cursor + length
                if len(self.data) < end + 2:
                    raise EOFError("Incomplete RESP2 bulk string")
                if self.data[end : end + 2] != b"\r\n":
                    raise ValueError("Missing RESP2 bulk string terminator")
                value = BulkStrings(self.data[next_cursor:end])
                next_cursor = end + 2
        else:
            raise ValueError(f"Unsupported RESP2 prefix: {prefix!r}")

        self.cursor = next_cursor
        return value
