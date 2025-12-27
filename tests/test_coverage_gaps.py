
import pytest
import sys
from pathlib import Path
from digpipe import pipeline
from digpipe.sinks.frame_log import FrameLogSink
from digpipe.types import Action

def test_pipeline_invalid_components():
    with pytest.raises(ValueError, match="Unknown source"):
        pipeline.get_source("invalid-source", 100)
        
    with pytest.raises(ValueError, match="Unknown mapper"):
        pipeline.get_mapper("invalid-mapper")
        
    with pytest.raises(ValueError, match="Unknown sink"):
        pipeline.get_sink("invalid-sink", "out.txt")

def test_pipeline_missing_tape(tmp_path):
    tape_dir = tmp_path / "nonexistent_tape"
    with pytest.raises(FileNotFoundError):
        pipeline.run_rendering(
            tape_path=str(tape_dir),
            mapper_name="gba-tenkey",
            sink_name="frame-log",
            output_path="out.txt"
        )

def test_framelog_sink_stdout(capsys):
    sink = FrameLogSink("-")
    action = Action(frame=1, device="dev", control="btn", value=1)
    sink.write_actions([action])
    
    captured = capsys.readouterr()
    assert "1: dev.btn=1\n" in captured.out
    
    # Close stdout sink (should not close actual stdout)
    sink.close()
    
def test_framelog_sink_closed_write(tmp_path):
    out_file = tmp_path / "out.log"
    sink = FrameLogSink(str(out_file))
    sink.close()
    
    action = Action(frame=1, device="dev", control="btn", value=1)
    with pytest.raises(RuntimeError, match="Sink is closed"):
        sink.write_actions([action])

def test_pi_source_old_python_compat(monkeypatch):
    """Test that PiDigitSource handles missing sys.set_int_max_str_digits gracefully."""
    import digpipe.sources.pi_chudnovsky as pi_mod
    
    # Simulate older python by removing the attribute from sys if it exists
    monkeypatch.delattr(sys, "set_int_max_str_digits", raising=False)
    
    # Initialize and run a small chunk generation
    source = pi_mod.PiDigitSource(10)
    # We just need to trigger the chunks method logic
    chunks = list(source.chunks(5))
    assert len(chunks) > 0
