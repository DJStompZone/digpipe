# DigPipe

Modular Decimal-Digit Input Pipeline for GBA Emulation

![GitHub License](https://img.shields.io/github/license/djstompzone/digpipe)
[![PyPI - Version](https://img.shields.io/pypi/v/digpipe?logo=pypi&logoColor=yellow&label=PyPi%20%7C%20Latest&link=https%3A%2F%2Fpypi.org%2Fproject%2Fdigpipe%2F)](https://pypi.org/project/digpipe/)

[![CI](https://github.com/DJStompZone/digpipe/actions/workflows/ci.yml/badge.svg)](https://github.com/DJStompZone/digpipe/actions/workflows/ci.yml) [![CD](https://github.com/DJStompZone/digpipe/actions/workflows/cd.yml/badge.svg)](https://github.com/DJStompZone/digpipe/actions/workflows/cd.yml) [![CodeQL Advanced](https://github.com/DJStompZone/digpipe/actions/workflows/codeql.yml/badge.svg)](https://github.com/DJStompZone/digpipe/actions/workflows/codeql.yml) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/digpipe)

## Overview

**DigPipe** is a modular pipeline for generating decimal digits, storing them in chunked binary tapes, mapping digits to abstract actions, and rendering those actions for emulation workflows.

**Context:** DigPipe powers a larger experiment where consecutive digits of π "play" video games. Gameplay traces are later analyzed for emergent behavior.

### Pipeline at a glance

```
DigitSource → DigitTape → DigitMapper → InputSink
```

- **DigitSource:** Generates decimal digits in fixed-size chunks (default: π via Chudnovsky with integer arithmetic). The stream starts with the leading `3` before the fractional digits.
- **DigitTape:** Persists chunks as packed nibbles (2 digits/byte) on disk, with one file per chunk.
- **DigitMapper:** Translates digits to abstract controls. Included mapper: GBA ten-key (digits `0–9` → `A, B, L, R, UP, DOWN, LEFT, RIGHT, START, SELECT`).
- **InputSink:** Emits mapped actions. Included sink: frame-log writer (line-per-action, `FRAME: DEVICE.CONTROL=VALUE`).

All layers are chunked and can resume mid-stream by chunk index. Exact integer math is used throughout digit generation.

See the [class diagram](docs/CLASS_DIAGRAM.md) for a structural overview of the concrete implementations and protocols.

## Quick start

```bash
# 1) Install (from PyPI)
pip install digpipe

# 2) Generate a digit tape (50 digits, chunks of 10 digits each)
digpipe generate --source pi --digits 50 --chunk-size 10 --out tape/

# 3) Render the tape to a frame log using the GBA ten-key mapper
digpipe render --tape tape/ --mapper gba-tenkey --sink frame-log --out inputs.log
```

## Installation

- **PyPI:** `pip install digpipe`
- **From source:** clone the repository, then `poetry install` (requires Python 3.10+).

The CLI entry point is `digpipe`; you can also run `python -m digpipe` for the same interface.

## Usage

### Generate digits to tape

```bash
digpipe generate \
  --source pi \
  --digits 1000000 \
  --chunk-size 1000 \
  --out tape/
```

Key details:

- `--source pi`: Uses the Chudnovsky integer implementation. `--digits` counts from the leading `3` (e.g., `--digits 5` yields `31415`).
- `--chunk-size`: Number of digits per chunk file. **Must be even** (packed storage writes two digits per byte) or generation will fail before writing.
- `--out`: Target directory. `header.json` is created alongside chunk files named `chunk_000000.dgt`, `chunk_000001.dgt`, etc. If the directory is missing it is created.

### Render a tape to actions

```bash
digpipe render \
  --tape tape/ \
  --mapper gba-tenkey \
  --sink frame-log \
  --out inputs.log
```

What happens:

- The pipeline reads sequential chunk files from `--tape`.
- `GbaTenKeyMapper` emits press/release pairs for each digit using the configured hold/release timings (defaults: 5 frames each).
- `FrameLogSink` writes `FRAME: gba.CONTROL=VALUE` lines to `--out` (or stdout when `-`).

### Resume rendering from a later chunk

Supply `--start-chunk` to skip already-processed chunks (e.g., after a partial run):

```bash
digpipe render --tape tape/ --mapper gba-tenkey --sink frame-log --out resumed.log --start-chunk 5
```

Chunks are zero-indexed. The example above skips chunks `0–4` and begins rendering with `chunk_000005.dgt`.

### Run tests and coverage

```bash
poetry run pytest            # unit tests
poetry run coverage run -m pytest
poetry run coverage report   # summary
```

## Tape format

- **Layout:** `header.json` (metadata placeholder) plus chunk files named `chunk_XXXXXX.dgt` under the tape directory.
- **Encoding:** Packed nibbles; each byte stores two digits. Only digit values `0–9` are valid.
- **Chunk rules:** Chunk sizes must be even; attempting to write odd-sized chunks or digits outside `0–9` raises errors.

## Agents

Coding agents and other automated tools should refer to [AGENTS.md](AGENTS.md) for complete project requirements and instructions.
