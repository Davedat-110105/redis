from src.redis_python.protocols.parser import Decoder
from src.redis_python.protocols.types import BulkStrings, Integers, SimpleString


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
