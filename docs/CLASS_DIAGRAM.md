# DigPipe Class Diagram

```mermaid
classDiagram
    class DigitChunk {
      int index
      bytes digits
    }
    class Action {
      str device
      str control
      int value
      int frame
    }

    class DigitSource {
      +chunks(chunk_size) Iterator~DigitChunk~
    }
    class PiDigitSource {
      +chunks(chunk_size) Iterator~DigitChunk~
    }
    DigitSource <|.. PiDigitSource

    class DigitTape {
      +write_chunk(chunk: DigitChunk)
      +read_chunk(index: int) DigitChunk
      +exists(index: int) bool
    }
    class FileDigitTape {
      +write_chunk(chunk: DigitChunk)
      +read_chunk(index: int) DigitChunk
      +exists(index: int) bool
    }
    DigitTape <|.. FileDigitTape

    class DigitMapper {
      +map_chunk(chunk: DigitChunk, start_frame: int) (List~Action~, int)
    }
    class GbaTenKeyMapper {
      -hold_frames: int
      -release_frames: int
      +map_chunk(chunk: DigitChunk, start_frame: int) (List~Action~, int)
    }
    DigitMapper <|.. GbaTenKeyMapper

    class InputSink {
      +write_actions(actions: Iterable~Action~)
      +close()
    }
    class FrameLogSink {
      -file_path: str
      -file: TextIO
      +write_actions(actions: Iterable~Action~)
      +close()
    }
    InputSink <|.. FrameLogSink

    class pipeline {
      +run_generation(source_name, total_digits, chunk_size, tape_path)
      +run_rendering(tape_path, mapper_name, sink_name, output_path, start_chunk)
    }
    class cli {
      +main()
    }

    pipeline --> DigitSource : factory (get_source)
    pipeline --> DigitMapper : factory (get_mapper)
    pipeline --> InputSink : factory (get_sink)
    pipeline --> FileDigitTape : reads/writes
    cli --> pipeline : delegates commands
```

**Notes**

- Chunk indices are zero-based. `run_rendering(..., start_chunk=n)` begins with `chunk_nnnnnn.dgt`.
- `PiDigitSource` includes the leading `3` when counting digits (e.g., `--digits 5` yields `31415`). Guard digits are internal and never emitted.
- `FileDigitTape` enforces even-length chunks and digit values `0–9`; invalid inputs raise `ValueError`.
