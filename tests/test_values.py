import pytest
from src.redis_python.protocols.values import (
    Array,
    BulkString,
    Integer,
    RESPValue,
    SimpleError,
    SimpleString,
)

def test_simple_string():
    assert SimpleString("OK").data == "OK"

def test_simple_error():
    assert SimpleError("ERR unknown command").data == "ERR unknown command"

def test_integer():
    assert Integer(-1).data == -1

def test_bulk_string():
    assert BulkString(b"\xc3\xa9").length == 2
    assert BulkString(b"hello").length == 5
    assert BulkString(None).length == -1
    assert BulkString(b"a\r\nb").length == 4

@pytest.mark.parametrize(
    ("data", "expected_length"),
    [
        pytest.param(None, -1, id="null"),
        pytest.param([], 0, id="empty"),
        pytest.param([BulkString(b"hello"), Integer(1)], 2, id="element-count"),
        pytest.param([Array([Integer(1), Integer(2)])], 1, id="nested-array"),
    ],
)
def test_array_length(data: list[RESPValue] | None, expected_length: int):
    value = Array(data)

    assert value.data is data
    assert value.length == expected_length


def test_type():
    pytest.raises(ValueError, SimpleString, "bad\r")
    pytest.raises(ValueError, SimpleError, "bad\n")
    pytest.raises(TypeError, Integer, True)
