import pytest
from src.redis_python.protocols.types import SimpleString, SimpleError, Integers, BulkStrings

def test_SimpleString():
    assert SimpleString("OK").data == "OK"

def test_SipleString():
    assert SimpleError("ERR unknown command").data == "ERR unknown command"

def test_Integers():
    assert Integers(-1).data == -1

def test_BulkString():
    assert BulkStrings(b"\xc3\xa9").length == 2
    assert BulkStrings(b"hello").length == 5
    assert BulkStrings(None).length == -1
    assert BulkStrings(b"a\r\nb").length == 4

def test_Type():
    pytest.raises(ValueError, SimpleString, "bad\r")
    pytest.raises(ValueError, SimpleError, "bad\n")
    pytest.raises(TypeError, Integers, True)
