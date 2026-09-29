from typing_extensions import Any, List


class Store:
    """Store string values in memory with linear-time key lookups."""

    def __init__(self):
        self.data: List = []

    def SET(self, key: str, value: str) -> None:
        """Insert a key or replace its existing value."""
        index: int | None = self._find(key)
        if (index is not None):
            self.data[index] = {"key": key, "value": value}
            return
        else:
            self.data.append({"key": key, "value": value})


    def GET(self, key: str) -> Any | None:
        """Return the value for a key, or None if it is absent."""
        value: int | None = self._find(key)
        if (value is not None):
            return self.data[value]["value"]
        else:
            return None


    def DEL(self, key: str) -> bool:
        """Delete a key and report whether it existed."""
        value: int | None = self._find(key)
        if (value is not None):
            del self.data[value]
            return True
        else:
            return False

    def EXISTS(self, key: str) -> bool:
        """Return whether a key exists in the store."""
        return self._find(key) is not None

    def _find(self, key: str) -> int | None:
        """Return the index of a key, or None if it is absent."""
        for (index, element) in enumerate(self.data):
            if (element["key"] == key):
                return index
        return None
