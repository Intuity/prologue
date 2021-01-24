# Copyright 2020, Peter Birch, mailto:peter@lightlogic.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import choice, randint
from unittest.mock import MagicMock, call

import pytest

from prologue.block import Block
from prologue.common import PrologueError
from prologue.directives.base import BlockDirective

from .common import random_str

def test_block_directive():
    """ Test the base block directive """
    parent    = {}
    yield_val = choice((True, False))
    block_dir = BlockDirective(parent=parent, yields=yield_val)
    # Sanity check
    assert block_dir.parent == parent
    assert block_dir.yields == yield_val
    assert not block_dir.opened and not block_dir.closed
    # Open the directive
    block_dir.open(random_str(5, 10), random_str(10, 20))
    o_lines   = [random_str(30, 50, spaces=True) for _x in range(10)]
    all_lines = o_lines[:]
    for line in o_lines: block_dir.append(line)
    assert block_dir.opened and not block_dir.closed
    # Trigger multiple transitions
    for _x in range(randint(1, 10)):
        block_dir.transition(random_str(5, 10), random_str(10, 20))
        t_lines    = [random_str(30, 50, spaces=True) for _x in range(10)]
        all_lines += t_lines
        for line in t_lines: block_dir.append(line)
        assert block_dir.opened and not block_dir.closed
    # Close the directive
    block_dir.close(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and block_dir.closed
    # Check all lines were appended to the base block
    assert block_dir.content == all_lines

def test_block_directive_multi_open():
    """ Try to open the block directive multiple times """
    parent    = {}
    yield_val = choice((True, False))
    block_dir = BlockDirective(parent=parent, yields=yield_val)
    # Sanity check
    assert block_dir.parent == parent
    assert block_dir.yields == yield_val
    assert not block_dir.opened and not block_dir.closed
    # Open the block
    block_dir.open(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and not block_dir.closed
    # Now try to open the block again
    for _x in range(100):
        with pytest.raises(PrologueError) as excinfo:
            block_dir.open(random_str(5, 10), random_str(10, 20))
        assert "Multiple opening statements for block detected" == str(excinfo.value)

def test_block_directive_bad_transition():
    """ Try transitions before opening block and after closing block """
    parent    = {}
    yield_val = choice((True, False))
    block_dir = BlockDirective(parent=parent, yields=yield_val)
    # Sanity check
    assert block_dir.parent == parent
    assert block_dir.yields == yield_val
    assert not block_dir.opened and not block_dir.closed
    # Try to perform transitions before opening block
    for _x in range(100):
        t_tag = random_str(5, 10)
        with pytest.raises(PrologueError) as excinfo:
            block_dir.transition(t_tag, random_str(10, 20))
        assert f"Transition '{t_tag}' used before opening directive" == str(excinfo.value)
    # Open the block
    block_dir.open(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and not block_dir.closed
    # Close the block
    block_dir.close(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and block_dir.closed
    # Try to perform transitions after closing block
    for _x in range(100):
        t_tag = random_str(5, 10)
        with pytest.raises(PrologueError) as excinfo:
            block_dir.transition(t_tag, random_str(10, 20))
        assert f"Transition '{t_tag}' used after closing directive" == str(excinfo.value)

def test_block_directive_multi_close():
    """ Try to close the block directive multiple times """
    parent    = {}
    yield_val = choice((True, False))
    block_dir = BlockDirective(parent=parent, yields=yield_val)
    # Sanity check
    assert block_dir.parent == parent
    assert block_dir.yields == yield_val
    assert not block_dir.opened and not block_dir.closed
    # Open the block
    block_dir.open(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and not block_dir.closed
    # Close the block
    block_dir.close(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and block_dir.closed
    # Now try to open the block again
    for _x in range(100):
        with pytest.raises(PrologueError) as excinfo:
            block_dir.close(random_str(5, 10), random_str(10, 20))
        assert "Multiple closing statements for block detected" == str(excinfo.value)

def test_block_directive_bad_append():
    """ Try appending before opening block and after closing block """
    parent    = {}
    yield_val = choice((True, False))
    block_dir = BlockDirective(parent=parent, yields=yield_val)
    # Sanity check
    assert block_dir.parent == parent
    assert block_dir.yields == yield_val
    assert not block_dir.opened and not block_dir.closed
    # Try to append to the block
    for _x in range(100):
        with pytest.raises(PrologueError) as excinfo:
            block_dir.append(random_str(30, 50, spaces=True))
        assert "Trying to append a line to an unopened directive" == str(excinfo.value)
    # Open the block
    block_dir.open(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and not block_dir.closed
    # Close the block
    block_dir.close(random_str(5, 10), random_str(10, 20))
    assert block_dir.opened and block_dir.closed
    # Try to append after closing block
    for _x in range(100):
        with pytest.raises(PrologueError) as excinfo:
            block_dir.append(random_str(30, 50, spaces=True))
        assert "Trying to append a line to a closed directive" == str(excinfo.value)
