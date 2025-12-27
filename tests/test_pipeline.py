import pytest
import sys
from io import StringIO
from pathlib import Path
from digpipe import pipeline
from digpipe.types import DigitChunk
from digpipe.digtape import FileDigitTape

import tempfile
import shutil

def test_end_to_end_integration():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        tape_dir = tmp_path / "tape"
        out_log = tmp_path / "out.log"
        
        # 1. Generate small tape
        # 50 digits, chunk size 10
        pipeline.run_generation("pi", 50, 10, str(tape_dir))
        
        assert (tape_dir / "header.json").exists()
        assert (tape_dir / "chunk_000000.dgt").exists()
        assert (tape_dir / "chunk_000004.dgt").exists()
        
        # 2. Render
        pipeline.run_rendering(str(tape_dir), "gba-tenkey", "frame-log", str(out_log))
        
        assert out_log.exists()
        content = out_log.read_text("utf-8")
        assert "gba." in content
        # 50 digits * 2 actions = 100 lines
        assert len(content.splitlines()) == 100

def test_rendering_offset():
    """Verify ability to start rendering from an arbitrary chunk."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        tape_dir = tmp_path / "tape_offset"
        out_log = tmp_path / "offset.log"
        
        # Generate 50 digits, chunk 10. Chunks 0, 1, 2, 3, 4.
        pipeline.run_generation("pi", 50, 10, str(tape_dir))
        
        # We want to start at Chunk 2 (digits 20-29).
        pipeline.run_rendering(str(tape_dir), "gba-tenkey", "frame-log", str(out_log), start_chunk=2)
        
        content = out_log.read_text("utf-8")
        lines = content.splitlines()
        
        # Should have processed chunks 2, 3, 4 (3 chunks = 30 digits = 60 lines)
        assert len(lines) == 60
        
        # The first action should correspond to the first digit of Chunk 2.
        # Pi: 3.1415926535 8979323846 2643383279 ...
        # Chunk 0: 3141592653
        # Chunk 1: 5897932384
        # Chunk 2: 6264338327
        # First digit of Chunk 2 is '6'.
        # 6 maps to LEFT (in gba_tenkey: 0123456 -> 6=LEFT)
        
        first_line = lines[0]
        assert "gba.LEFT=1" in first_line
