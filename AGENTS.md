# DigPipe

Modular Decimal-Digit Input Pipeline for GBA Emulation

## Agent Instructions

This file is intented to serve as the authoritative instruction set for all LLMs, intern simulacra, and other various agentic contributors. If you are an LLM or similar, please ensure you fully read and understand the contents of this file before contributing to the project.

## Primary Project Context

This is part of a larger project which aims to allow consecutive digits of pi to "play" video games. The gameplay will then be analyzed in an attempt to identify any emergent behaviors or patterns observed.

## Core Design Principles (MANDATORY)

* **Modularity first**: every stage must be swappable.
* **Chunked processing**: no unbounded growth of integers or buffers.
* **No heuristics / no floating-point rounding**: all math must be exact.
* **Streaming-friendly**: support “generate → store → map → emit” without giant intermediate files.
* **Future-proof**: emulator formats must be adapters, not baked into core logic.

## Pipeline Architecture

The pipeline consists of **four orthogonal layers**:

```
DigitSource → DigitTape → DigitMapper → InputSink
```

Each layer MUST be implemented as a clean interface with no hidden coupling.



[ ================= DigitSource ================= ]: #

### DigitSource

Decimal digit generator

#### Responsibility

Produce **decimal digits 0–9** in **fixed-size chunks**, sequentially.

#### Interface

```python
class DigitSource(Protocol):
    def chunks(self, chunk_digits: int) -> Iterator[DigitChunk]: ...
```

#### Initial implementation

* **PiDigitSource** using **Chudnovsky + binary splitting**
* Uses **integer fixed-point arithmetic** only
* Uses **guard digits** internally but only emits stable digits
* MUST support generation of arbitrarily many digits via chunking

#### Constraints

* No floating point
* No global “big remainder” that grows forever
* Chunk generation must not depend on previously emitted chunks except via explicit state




[ ================= DigitTape ================= ]: #

### DigitTape

DigPipe's de facto storage format

#### Responsibilities

Store decimal digits efficiently and independently of emulator logic.

* write digit chunks
* read digit chunks
* validate chunk integrity
* support partial / resumed generation

Digits MUST be stored as digits (0–9), **not button names or emulator codes**.

#### Requirements

* Use **packed nibbles** (2 digits per byte, 4 bits per digit)
* Chunked storage (each chunk independently readable/verifiable)
* Optional per-chunk checksum (CRC32 or xxHash)
* Simple, explicit on-disk format

#### Recommended structure

```
tape/
  header.json
  chunk_000000.dgt
  chunk_000001.dgt
  ...
```


[ ================= DigitMapper ================= ]: #

### DigitMapper

Digits → abstract actions

#### Responsibility

Map digits 0–9 to **abstract input actions** with timing.

#### Example mapping (initial target: GBA)

Digits map to 10 controls:

```
0–9 → A, B, L, R, UP, DOWN, LEFT, RIGHT, START, SELECT
```

#### Timing model (choose one, but make it configurable)

* Default: **press for N frames, release for M frames**
* Frame-based timing only (no real-time clocks)

#### Interface

```python
class DigitMapper(Protocol):
    def map_chunk(
        self,
        chunk: DigitChunk,
        start_frame: int
    ) -> tuple[list[Action], int]: ...
```

#### Action model

Actions must be **abstract**, e.g.:

```python
Action(
    device="gba",
    control="A",
    value=1,
    frame=123456
)
```

NO emulator-specific assumptions here.


[ ================= InputSink ================= ]: #

### InputSink

Output adapters

#### Responsibility

Serialize abstract actions into some output format.

#### Initial implementation

* **Plain frame-log sink** (text or binary)

  * One line per frame or per action
  * Human-readable and debuggable
* This is the reference sink used for testing

#### Future sinks (not required yet, but design must allow):

* BizHawk `.bk2`
* mGBA TAS / scripting
* RetroArch Lua input driver
* Live injection (out of scope)

#### Interface

```python
class InputSink(Protocol):
    def write_actions(self, actions: Iterable[Action]) -> None: ...
    def close(self) -> None: ...
```

### Chunking Strategy (CRITICAL)

* All layers operate on **chunks** (e.g., 1M–50M digits)
* No layer may assume the full digit stream exists in memory
* Chunk boundaries must be clean and deterministic
* The pipeline must be able to resume at chunk N without redoing earlier work

### Correctness Guarantees

* Decimal digits MUST be exact (validated against known π sources).
* Any comparison must use **fixed-point integer math**.
* Guard digits must be used internally but never emitted.
* No “digit stability heuristics” allowed.

### Performance Expectations

* No quadratic behavior from growing integers
* Generation must scale linearly *per chunk*
* Emission/storage must be sequential I/O
* No gigantic Python strings of all digits

### Deliverables

#### Required modules

* `digtape.py` — chunked packed-digit storage
* `sources/pi_chudnovsky.py` — decimal digit generator
* `mappers/gba_tenkey.py` — digit → 10-button mapping
* `sinks/frame_log.py` — reference output sink
* `pipeline.py` — composition / driver
* `cli.py` — command-line interface

#### CLI examples

```bash
## Generate digit tape
digpipe generate \
  --source pi \
  --digits 100000000 \
  --chunk-size 1000000 \
  --out tape/

## Render inputs
digpipe render \
  --tape tape/ \
  --mapper gba-tenkey \
  --sink frame-log \
  --out inputs.log
```

### Code Quality Requirements

* Python 3.10+
* Type hints everywhere
* Protocols / dataclasses preferred
* No global state
* No print spam (use logging)
* Production-quality structure, not a demo
* Google python style guidelines ("""docstrings""", not #comments)
* SOLID principles

### Explicit Admonitions (DO NOT DO THESE)

* Do NOT store digits as text unless explicitly requested
* Do NOT bake emulator formats into core logic
* Do NOT generate a billion digits in a single Python integer
* Do NOT optimize prematurely with C unless justified later

### Future Goals

* Chunk index for random access
* Resume generation after crash
* Pluggable math sources (π, e, random, file)
* Parallel generation (future)

### Final Instruction

This is a **long-running, correctness-critical pipeline**.
Favor **clarity, invariants, and modularity** over cleverness.

If a design decision trades speed for correctness, **choose correctness**.

If you want, after Codex spins up the scaffold, you can bring it back here and I’ll:

* review architecture
* catch hidden big-O landmines
* or help you wire the first concrete GBA mapper/sink combo

This is going to be *fun*!
