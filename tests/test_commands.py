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