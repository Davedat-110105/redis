import pytest

from src.redis_python.protocols.encoder import RESPEncoder
from src.redis_python.protocols.parser import RESPParser
from src.redis_python.protocols.values import (
    BulkString,
    Integer,
    RESPValue,
    SimpleError,
    SimpleString,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(SimpleString("OK"), b"+OK\r\n", id="simple-string"),
        pytest.param(SimpleString("café"), b"+caf\xc3\xa9\r\n", id="unicode-string"),
        pytest.param(Integer(-1), b":-1\r\n", id="negative-integer"),
        pytest.param(Integer(0), b":0\r\n", id="zero-integer"),
        pytest.param(Integer(42), b":42\r\n", id="positive-integer"),
        pytest.param(
            SimpleError("ERR unknown command"),
            b"-ERR unknown command\r\n",
            id="error",
        ),
        pytest.param(BulkString(b"hello"), b"$5\r\nhello\r\n", id="bulk-string"),
        pytest.param(BulkString(b""), b"$0\r\n\r\n", id="empty-bulk-string"),
        pytest.param(BulkString(None), b"$-1\r\n", id="null-bulk-string"),
        pytest.param(
            BulkString(b"\x00\xff\r\n"),
            b"$4\r\n\x00\xff\r\n\r\n",
            id="binary-bulk-string",
        ),
        pytest.param(
            BulkString(b"\xc3\xa9"),
            b"$2\r\n\xc3\xa9\r\n",
            id="multibyte-bulk-string",
        ),
    ],
)
def test_encode_resp_value(value: RESPValue, expected: bytes):
    assert RESPEncoder(value).encode() == expected


def test_encoded_values_can_be_parsed_consecutively():
    values: list[RESPValue] = [
        SimpleString("OK"),
        SimpleError("ERR unknown command"),
        Integer(-1),
        BulkString(b""),
        BulkString(None),
        BulkString(b"a\r\nb"),
    ]
    data = b"".join(RESPEncoder(value).encode() for value in values)
    parser = RESPParser(data)

    for expected in values:
        result = parser.parse()
        assert type(result) is type(expected)
        assert result.data == expected.data
    assert parser.cursor == len(data)
