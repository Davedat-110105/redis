from src.redis_python.store import Store


def test_set_then_get():
    store = Store()
    store.set(b"name", b"Huy")

    assert store.get(b"name") == b"Huy"


def test_set_overwrites_existing_value():
    store = Store()
    store.set(b"name", b"Huy")
    store.set(b"name", b"Dave")

    assert store.get(b"name") == b"Dave"


def test_get_missing_key_returns_none():
    assert Store().get(b"missing") is None


def test_keys_are_case_sensitive():
    store = Store()
    store.set(b"Name", b"Huy")

    assert store.get(b"name") is None


def test_exists():
    store = Store()
    store.set(b"name", b"Huy")

    assert store.exists(b"name") is True
    assert store.exists(b"missing") is False


def test_delete_existing_key():
    store = Store()
    store.set(b"name", b"Huy")

    assert store.delete(b"name") is True
    assert store.get(b"name") is None
    assert store.exists(b"name") is False


def test_delete_missing_key_returns_false():
    assert Store().delete(b"missing") is False


def test_values_are_binary_safe():
    store = Store()
    store.set(b"blob", b"\x00\xff\r\n")

    assert store.get(b"blob") == b"\x00\xff\r\n"
