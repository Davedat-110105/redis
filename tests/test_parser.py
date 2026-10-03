import pytest

from src.redis_python.protocols.parser import Decoder
from src.redis_python.protocols.types import BulkStrings, Integers, SimpleError, SimpleString


def test_decode_simple_string():
    result = Decoder(b"+OK\r\n").parsing()

    assert isinstance(result, SimpleString)
    assert result.data == "OK"


def test_decode_negative_integer():
    result = Decoder(b":-1\r\n").parsing()

    assert isinstance(result, Integers)
    assert result.data == -1


def test_decode_bulk_string():
    result = Decoder(b"$6\r\nfoobar\r\n").parsing()

    assert isinstance(result, BulkStrings)
    assert result.data == b"foobar"
    assert result.length == 6


def test_decode_bulk_string_containing_crlf():
    result = Decoder(b"$4\r\na\r\nb\r\n").parsing()

    assert isinstance(result, BulkStrings)
    assert result.data == b"a\r\nb"


def test_decode_null_bulk_string():
    result = Decoder(b"$-1\r\n").parsing()

    assert isinstance(result, BulkStrings)
    assert result.data is None
    assert result.length == -1


def test_decode_empty_bulk_string():
    result = Decoder(b"$0\r\n\r\n").parsing()

    assert isinstance(result, BulkStrings)
    assert result.data == b""
    assert result.length == 0


def test_decode_error_reply():
    result = Decoder(b"-ERR unknown command\r\n").parsing()

    assert isinstance(result, SimpleError)
    assert result.data == "ERR unknown command"


def test_decode_consecutive_values():
    decoder = Decoder(b"+OK\r\n:-1\r\n$4\r\na\r\nb\r\n")

    assert decoder.parsing().data == "OK"
    assert decoder.cursor == 5
    assert decoder.parsing().data == -1
    assert decoder.parsing().data == b"a\r\nb"
    assert decoder.cursor == len(decoder.data)
    with pytest.raises(EOFError):
        decoder.parsing()


@pytest.mark.parametrize("data", [b"+OK", b"$5\r\nabc"])
def test_incomplete_value_does_not_advance_cursor(data: bytes):
    decoder = Decoder(data)

    with pytest.raises(EOFError):
        decoder.parsing()
    assert decoder.cursor == 0


@pytest.mark.parametrize(
    "data",
    [b"+bad\nvalue\r\n", b":nope\r\n", b"$-2\r\n", b"$3\r\nheyXX", b"?x\r\n"],
)
def test_invalid_value_does_not_advance_cursor(data: bytes):
    decoder = Decoder(data)

    with pytest.raises(ValueError):
        decoder.parsing()
    assert decoder.cursor == 0
