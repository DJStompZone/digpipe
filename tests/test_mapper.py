"""Tests for GbaTenKeyMapper."""

import pytest
from digpipe.mappers.gba_tenkey import GbaTenKeyMapper
from digpipe.types import DigitChunk

def test_mapping_values():
    mapper = GbaTenKeyMapper()
    # 0 -> A, 1 -> B
    chunk = DigitChunk(index=0, digits=bytes([0, 1]))
    actions, next_frame = mapper.map_chunk(chunk, start_frame=100)
    
    # 0 -> A
    assert actions[0].control == "A"
    assert actions[0].value == 1
    assert actions[0].frame == 100
    
    # Release A
    assert actions[1].control == "A"
    assert actions[1].value == 0
    assert actions[1].frame == 100 + 5
    
    # 1 -> B (starts 5 frames after release = 100 + 5 + 5 = 110)
    assert actions[2].control == "B"
    assert actions[2].value == 1
    assert actions[2].frame == 110
    
    assert actions[3].control == "B"
    assert actions[3].value == 0
    assert actions[3].frame == 115
    
    # Next frame should be 120
    assert next_frame == 120

def test_timing_config():
    mapper = GbaTenKeyMapper(hold_frames=10, release_frames=20)
    chunk = DigitChunk(index=0, digits=bytes([0]))
    
    actions, next_frame = mapper.map_chunk(chunk, start_frame=0)
    
    # Press at 0
    assert actions[0].frame == 0
    # Release at 10 (hold 10)
    assert actions[1].frame == 10
    # Next press would be at 10 + 20 = 30
    assert next_frame == 30
