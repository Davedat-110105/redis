from src.redis_python.store import Store


def test_SET():
    store = Store()
    assert store.SET("name", "Huy") == None

def test_EXIST():
    store = Store()
    store.SET("name", "Huy")
    store.SET("test", "10")
    assert store.EXISTS("name") == True

def test_DEL():
    store = Store()
    store.SET("name", "Huy")
    store.SET("test", "10")
    assert store.DEL("name") == True

def test_GET():
    store = Store()
    store.SET("name", "Huy")
    store.SET("test", "10")
    assert store.GET("name") == "Huy"
