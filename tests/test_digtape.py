"""Tests for DigTape storage."""

import pytest
from pathlib import Path
from digpipe.digtape import FileDigitTape
from digpipe.types import DigitChunk

import tempfile
import shutil

def test_round_trip():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tape = FileDigitTape(tmp_dir)
        
        # Chunk 0: 0, 1, ..., 9
        digits = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        chunk = DigitChunk(index=0, digits=digits)
        
        tape.write_chunk(chunk)
        
        read_back = tape.read_chunk(0)
        assert read_back.index == 0
        assert read_back.digits == digits

def test_odd_chunk_size_error():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tape = FileDigitTape(tmp_dir)
        # 3 digits (odd)
        digits = bytes([1, 2, 3])
        chunk = DigitChunk(index=1, digits=digits)
        
        with pytest.raises(ValueError, match="Chunk size must be even"):
            tape.write_chunk(chunk)

def test_invalid_digit_value():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tape = FileDigitTape(tmp_dir)
        # Digit 10 is invalid (must be 0-9)
        digits = bytes([0, 10])
        chunk = DigitChunk(index=2, digits=digits)
        
        with pytest.raises(ValueError, match="Invalid digits"):
            tape.write_chunk(chunk)

def test_missing_chunk():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tape = FileDigitTape(tmp_dir)
        assert not tape.exists(99)
        
        with pytest.raises(FileNotFoundError):
            tape.read_chunk(99)
