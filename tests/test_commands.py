import pytest

from src.redis_python.commands import CommandHandler
from src.redis_python.protocols.values import Array, BulkString
from src.redis_python.store import Store


def command(*words: bytes) -> Array:
    return Array([BulkString(word) for word in words])


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        pytest.param([b"PING"], b"+PONG\r\n", id="ping"),
        pytest.param([b"PING", b"hello"], b"$5\r\nhello\r\n", id="ping-with-message"),
        pytest.param([b"ECHO", b"hello"], b"$5\r\nhello\r\n", id="echo"),
        pytest.param([b"ping"], b"+PONG\r\n", id="lowercase-ping"),
        pytest.param([b"ECHO", b"Hello"], b"$5\r\nHello\r\n", id="echo-keeps-argument-case"),
        pytest.param(
            [b"ECHO"],
            b"-ERR wrong number of arguments for 'echo' command\r\n",
            id="echo-without-argument",
        ),
        pytest.param([b"FOO"], b"-ERR unknown command 'FOO'\r\n", id="unknown-command"),
        pytest.param([b"foo"], b"-ERR unknown command 'foo'\r\n", id="unknown-keeps-case"),
    ],
)
def test_handle(words: list[bytes], expected: bytes):
    handler = CommandHandler(Store())

    assert handler.handle(command(*words)).encode() == expected


def run(handler: CommandHandler, *words: bytes) -> bytes:
    return handler.handle(command(*words)).encode()


def test_set_replies_ok_and_writes_to_store():
    store = Store()
    handler = CommandHandler(store)

    assert run(handler, b"SET", b"name", b"Huy") == b"+OK\r\n"
    assert store.get(b"name") == b"Huy"


def test_get_returns_value_after_set():
    handler = CommandHandler(Store())
    run(handler, b"SET", b"name", b"Huy")

    assert run(handler, b"GET", b"name") == b"$3\r\nHuy\r\n"


def test_get_missing_key_returns_null_bulk_string():
    handler = CommandHandler(Store())

    assert run(handler, b"GET", b"missing") == b"$-1\r\n"


def test_set_overwrites_value():
    handler = CommandHandler(Store())
    run(handler, b"SET", b"name", b"Huy")
    run(handler, b"SET", b"name", b"Dave")

    assert run(handler, b"GET", b"name") == b"$4\r\nDave\r\n"


def test_del_returns_number_of_keys_removed():
    handler = CommandHandler(Store())
    run(handler, b"SET", b"a", b"1")
    run(handler, b"SET", b"b", b"2")

    assert run(handler, b"DEL", b"a", b"b", b"missing") == b":2\r\n"
    assert run(handler, b"GET", b"a") == b"$-1\r\n"


def test_exists_counts_every_existing_key_given():
    handler = CommandHandler(Store())
    run(handler, b"SET", b"a", b"1")

    assert run(handler, b"EXISTS", b"a", b"a", b"missing") == b":2\r\n"


@pytest.mark.parametrize(
    ("words", "name"),
    [
        pytest.param([b"SET", b"name"], "set", id="set-without-value"),
        pytest.param([b"GET"], "get", id="get-without-key"),
        pytest.param([b"GET", b"a", b"b"], "get", id="get-with-two-keys"),
        pytest.param([b"DEL"], "del", id="del-without-keys"),
        pytest.param([b"EXISTS"], "exists", id="exists-without-keys"),
    ],
)
def test_wrong_number_of_arguments(words: list[bytes], name: str):
    handler = CommandHandler(Store())
    expected = f"-ERR wrong number of arguments for '{name}' command\r\n".encode()

    assert run(handler, *words) == expected