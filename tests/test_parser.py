import pytest

from src.redis_python.protocols.parser import RESPParser
from src.redis_python.protocols.values import BulkString, Integer, SimpleError, SimpleString


def test_parse_simple_string():
    result = RESPParser(b"+OK\r\n").parse()

    assert isinstance(result, SimpleString)
    assert result.data == "OK"


def test_parse_negative_integer():
    result = RESPParser(b":-1\r\n").parse()

    assert isinstance(result, Integer)
    assert result.data == -1


def test_parse_bulk_string():
    result = RESPParser(b"$6\r\nfoobar\r\n").parse()

    assert isinstance(result, BulkString)
    assert result.data == b"foobar"
    assert result.length == 6


def test_parse_bulk_string_containing_crlf():
    result = RESPParser(b"$4\r\na\r\nb\r\n").parse()

    assert isinstance(result, BulkString)
    assert result.data == b"a\r\nb"


def test_parse_null_bulk_string():
    result = RESPParser(b"$-1\r\n").parse()

    assert isinstance(result, BulkString)
    assert result.data is None
    assert result.length == -1


def test_parse_empty_bulk_string():
    result = RESPParser(b"$0\r\n\r\n").parse()

    assert isinstance(result, BulkString)
    assert result.data == b""
    assert result.length == 0


def test_parse_error_reply():
    result = RESPParser(b"-ERR unknown command\r\n").parse()

    assert isinstance(result, SimpleError)
    assert result.data == "ERR unknown command"


def test_parse_consecutive_values():
    parser = RESPParser(b"+OK\r\n:-1\r\n$4\r\na\r\nb\r\n")

    assert parser.parse().data == "OK"
    assert parser.cursor == 5
    assert parser.parse().data == -1
    assert parser.parse().data == b"a\r\nb"
    assert parser.cursor == len(parser.data)
    with pytest.raises(EOFError):
        parser.parse()


@pytest.mark.parametrize("data", [b"+OK", b"$5\r\nabc"])
def test_incomplete_value_does_not_advance_cursor(data: bytes):
    parser = RESPParser(data)

    with pytest.raises(EOFError):
        parser.parse()
    assert parser.cursor == 0


@pytest.mark.parametrize(
    "data",
    [b"+bad\nvalue\r\n", b":nope\r\n", b"$-2\r\n", b"$3\r\nheyXX", b"?x\r\n"],
)
def test_invalid_value_does_not_advance_cursor(data: bytes):
    parser = RESPParser(data)

    with pytest.raises(ValueError):
        parser.parse()
    assert parser.cursor == 0
