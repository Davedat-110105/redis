import pytest
from src.redis_python.protocols.values import SimpleString, SimpleError, Integer, BulkString

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

def test_type():
    pytest.raises(ValueError, SimpleString, "bad\r")
    pytest.raises(ValueError, SimpleError, "bad\n")
    pytest.raises(TypeError, Integer, True)
