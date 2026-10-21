from src.redis_python.store import Store


def test_set():
    store = Store()
    assert store.set("name", "Huy") == None

def test_exists():
    store = Store()
    store.set("name", "Huy")
    store.set("test", "10")
    assert store.exists("name") == True

def test_delete():
    store = Store()
    store.set("name", "Huy")
    store.set("test", "10")
    assert store.delete("name") == True

def test_get():
    store = Store()
    store.set("name", "Huy")
    store.set("test", "10")
    assert store.get("name") == "Huy"
