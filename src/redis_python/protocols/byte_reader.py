"""Read raw bytes while keeping track of a position in the input buffer."""


class ByteReader:
    """Read bytes while tracking the next unread position.

    Successful reads advance the cursor. Failed reads leave it unchanged.
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.cursor = 0

    def read_line(self) -> bytes:
        """Read a line without CRLF, then advance past both terminator bytes."""
        start = self.cursor
        end = self.data.find(b"\r\n", start)
        if end == -1:
            raise EOFError("Incomplete CRLF-terminated line")
        line = self.data[start:end]
        if b"\r" in line or b"\n" in line:
            raise ValueError("Unexpected CR or LF inside line")
        self.cursor = end + 2
        return line

    def read_exact(self, count: int) -> bytes:
        """Read exactly count bytes, or raise EOFError without consuming any."""
        if count < 0:
            raise ValueError("Byte count must be non-negative")
        end = self.cursor + count
        if end > len(self.data):
            raise EOFError("Not enough bytes to read")
        chunk = self.data[self.cursor:end]
        self.cursor = end
        return chunk

    def mark(self) -> int:
        """Return the current position so a caller can restore it later."""
        return self.cursor

    def reset(self, position: int) -> None:
        """Restore a saved position within the buffer."""
        if not 0 <= position <= len(self.data):
            raise ValueError("Position is outside the buffer")
        self.cursor = position
