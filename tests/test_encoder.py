import pytest

from src.redis_python.protocols.encoder import Encoder
from src.redis_python.protocols.parser import Decoder
from src.redis_python.protocols.types import (
    BulkStrings,
    Integers,
    RESPValue,
    SimpleError,
    SimpleString,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(SimpleString("OK"), b"+OK\r\n", id="simple-string"),
        pytest.param(SimpleString("café"), b"+caf\xc3\xa9\r\n", id="unicode-string"),
        pytest.param(Integers(-1), b":-1\r\n", id="negative-integer"),
        pytest.param(Integers(0), b":0\r\n", id="zero-integer"),
        pytest.param(Integers(42), b":42\r\n", id="positive-integer"),
        pytest.param(
            SimpleError("ERR unknown command"),
            b"-ERR unknown command\r\n",
            id="error",
        ),
        pytest.param(BulkStrings(b"hello"), b"$5\r\nhello\r\n", id="bulk-string"),
        pytest.param(BulkStrings(b""), b"$0\r\n\r\n", id="empty-bulk-string"),
        pytest.param(BulkStrings(None), b"$-1\r\n", id="null-bulk-string"),
        pytest.param(
            BulkStrings(b"\x00\xff\r\n"),
            b"$4\r\n\x00\xff\r\n\r\n",
            id="binary-bulk-string",
        ),
        pytest.param(
            BulkStrings(b"\xc3\xa9"),
            b"$2\r\n\xc3\xa9\r\n",
            id="multibyte-bulk-string",
        ),
    ],
)
def test_encode_resp_value(value: RESPValue, expected: bytes):
    assert Encoder(value).convert() == expected


def test_encoded_values_can_be_decoded_consecutively():
    values: list[RESPValue] = [
        SimpleString("OK"),
        SimpleError("ERR unknown command"),
        Integers(-1),
        BulkStrings(b""),
        BulkStrings(None),
        BulkStrings(b"a\r\nb"),
    ]
    data = b"".join(Encoder(value).convert() for value in values)
    decoder = Decoder(data)

    for expected in values:
        result = decoder.parsing()
        assert type(result) is type(expected)
        assert result.data == expected.data
    assert decoder.cursor == len(data)
