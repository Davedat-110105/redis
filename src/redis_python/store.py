from typing_extensions import Any, List


class Store:
    def __init__(self):
        # This is a sample shape of the data
        # [
        #     {"key": "name", "value": "Dave"},
        #     {"key": "age", "value": 21}
        # ]
        self.data: List = []

    """Add or update value in a store"""
    def SET(self, key: str, value: str) -> None:
        index: int | None = self._find(key)
        if (index is not None):
            self.data[index] = {"key": key, "value": value}
            return
        else:
            self.data.append({"key": key, "value": value})


    """Get value by keys and return pairs"""
    def GET(self, key: str) -> Any | None:
        # Check if exist
        value: int | None = self._find(key)
        if (value is not None):
            return self.data[value]["value"]
        else:
            return None


    def DEL(self, key: str) -> bool:
        value: int | None = self._find(key)
        if (value is not None):
            del self.data[value]
            return True
        else:
            return False

    def EXISTS(self, key: str) -> bool:
        return self._find(key) is not None

    def _find(self, key: str) -> int | None:
        for (index, element) in enumerate(self.data):
            if (element["key"] == key):
                return index
        return None
