class Store:
    """Store byte values in memory, keyed by bytes."""

    def __init__(self) -> None:
        self.data: dict[bytes, bytes] = {}

    def set(self, key: bytes, value: bytes) -> None:
        """Insert a key or replace its existing value."""
        self.data[key] = value

    def get(self, key: bytes) -> bytes | None:
        """Return the value for a key, or None if it is absent."""
        return self.data.get(key)

    def delete(self, key: bytes) -> bool:
        """Delete a key and report whether it existed."""
        if key not in self.data:
            return False
        del self.data[key]
        return True

    def exists(self, key: bytes) -> bool:
        """Return whether a key exists in the store."""
        return key in self.data
