"""Tests for PiDigitSource."""

import pytest
from digpipe.sources.pi_chudnovsky import PiDigitSource

# First 100 digits of Pi (after 3.)
PI_100 = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

def test_pi_correctness():
    # Generate 100 digits
    source = PiDigitSource(total_digits=100)
    chunks = list(source.chunks(chunk_size=50))
    
    assert len(chunks) == 2
    
    # Reconstruct digits
    emitted_bytes = b"".join(c.digits for c in chunks)
    emitted_str = "".join(str(d) for d in emitted_bytes)
    
    # PiDigitSource emits digits *after* 3. (decimal digits) 
    # Logic in implementation: `pi_int` includes the 3?
    # No, `pi_int` is `314159...`.
    # `full_str` is "314159...".
    # `chunks` emits bytes of these chars.
    # So chunk 0 starts with 3, 1, 4...
    
    # User requirement: "Generates decimal digits (0–9) from a mathematical source (initially π)."
    # Usually we want the fractional digits?
    # AGENTS.md: "Decimal digit generator... Produce decimal digits 0–9... 3.14159..."
    # If the tape is used for input, does the '3' matter?
    # Usually "digits of Pi" implies 3 is included or excluded?
    # My implementation does: `full_str = str(pi_int)` -> "314159..."
    # So index 0 is '3'.
    
    expected = "3" + PI_100
    expected = expected[:100] # total 100
    
    assert emitted_str == expected

def test_chunking_exact():
    source = PiDigitSource(total_digits=10)
    chunks = list(source.chunks(chunk_size=2))
    assert len(chunks) == 5
    for c in chunks:
        assert len(c.digits) == 2
