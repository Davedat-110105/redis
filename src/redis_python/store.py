from typing_extensions import Any, List


class Store:
    def __init__(self):
        self.data: List = []

    """Add or update value in a store"""
    def SET(self, value: dict) -> None:
        self.data.append(value)

    """Get value by keys and return pairs"""
    def GET(self, key: str) -> Any:
        for element in self.data:
            if (element[key]):
                return element[key]
            else:
                return {}

    def DEL(self, key: str) -> bool:
        for element in self.data:
            if (element[key]):
                self.data.remove(element[key])
                return True
        return False
