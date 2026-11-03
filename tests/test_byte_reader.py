import pytest

from src.redis_python.protocols.byte_reader import ByteReader


def test_read_line_continues_after_the_previous_terminator():
    reader = ByteReader(b"5\r\nhello\r\n")

    assert reader.read_line() == b"5"
    assert reader.cursor == 3
    assert reader.read_line() == b"hello"
    assert reader.cursor == 10


def test_read_line_accepts_an_empty_line():
    reader = ByteReader(b"\r\nnext\r\n")

    assert reader.read_line() == b""
    assert reader.cursor == 2
    assert reader.read_line() == b"next"


@pytest.mark.parametrize("tail", [b"", b"unfinished", b"unfinished\r"])
def test_incomplete_line_preserves_the_current_position(tail):
    reader = ByteReader(b"OK\r\n" + tail)
    assert reader.read_line() == b"OK"

    with pytest.raises(EOFError):
        reader.read_line()

    assert reader.cursor == 4


@pytest.mark.parametrize("line", [b"bad\nline\r\n", b"bad\rline\r\n"])
def test_invalid_line_preserves_the_current_position(line):
    reader = ByteReader(b"OK\r\n" + line)
    assert reader.read_line() == b"OK"

    with pytest.raises(ValueError):
        reader.read_line()

    assert reader.cursor == 4


def test_exact_reads_preserve_binary_payloads_between_line_reads():
    reader = ByteReader(b"$5\r\na\r\n\x00\xff\r\n")

    assert reader.read_exact(1) == b"$"
    assert reader.read_line() == b"5"
    assert reader.read_exact(5) == b"a\r\n\x00\xff"
    assert reader.read_exact(2) == b"\r\n"
    assert reader.cursor == 11


def test_incomplete_exact_read_does_not_consume_available_bytes():
    reader = ByteReader(b"abc")
    assert reader.read_exact(1) == b"a"

    with pytest.raises(EOFError):
        reader.read_exact(3)

    assert reader.cursor == 1
    assert reader.read_exact(2) == b"bc"


def test_exact_read_at_end_raises_eof():
    reader = ByteReader(b"")

    with pytest.raises(EOFError):
        reader.read_exact(1)

    assert reader.cursor == 0


def test_zero_length_read_succeeds_at_end():
    reader = ByteReader(b"a")
    assert reader.read_exact(1) == b"a"

    assert reader.read_exact(0) == b""
    assert reader.cursor == 1


def test_negative_length_is_rejected_without_moving():
    reader = ByteReader(b"abc")
    assert reader.read_exact(1) == b"a"

    with pytest.raises(ValueError):
        reader.read_exact(-1)

    assert reader.cursor == 1


def test_reset_restores_a_mark_after_an_incomplete_sequence():
    reader = ByteReader(b"OK\r\n$5\r\nhel")
    assert reader.read_line() == b"OK"
    start = reader.mark()
    assert reader.read_exact(1) == b"$"
    assert reader.read_line() == b"5"

    with pytest.raises(EOFError):
        reader.read_exact(5)
    reader.reset(start)

    assert reader.cursor == 4
    assert reader.read_exact(1) == b"$"
    assert reader.read_line() == b"5"


@pytest.mark.parametrize("position", [-1, 4])
def test_reset_rejects_positions_outside_the_buffer(position):
    reader = ByteReader(b"abc")
    assert reader.read_exact(1) == b"a"

    with pytest.raises(ValueError):
        reader.reset(position)

    assert reader.cursor == 1
