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

import pytest

from prologue.block import Block
from prologue.directives.base import Directive
from prologue.common import PrologueError

def test_block_stack():
    """ Check a block is aware of its parent and can navigate the stack """
    # Construct a basic chain
    top = Block(None)
    mid = Block(top)
    btm = Block(mid)
    # Check the basic parent pointers
    assert top.parent == None
    assert mid.parent == top
    assert btm.parent == mid
    # Check that the stack returns the correct entries
    assert top.stack == [top]
    assert mid.stack == [top, mid]
    assert btm.stack == [top, mid, btm]

def test_block_contents():
    """ Test that contents can be pushed into and read back from a block """
    class MockDirective(Directive):
        def evaluate(self, ctx):
            yield "MockDirA"
            yield "MockDirB"
    block = Block(None)
    block.append("Line 1")
    block.append("Line 2")
    block.append(MockDirective(block))
    block.append("Line 3")
    block.append("Line 4")
    result = [x for x in block.evaluate(None)]
    assert result[0] == "Line 1"
    assert result[1] == "Line 2"
    assert result[2] == "MockDirA"
    assert result[3] == "MockDirB"
    assert result[4] == "Line 3"
    assert result[5] == "Line 4"

def test_block_bad_content():
    """ Try to append a bad entry to a block """
    class BadClass: pass
    block = Block(None)
    # Try appending a a bad object
    with pytest.raises(PrologueError) as excinfo:
        block.append(BadClass())
    assert "Entry must be a string or Block, not BadClass" in str(excinfo.value)
    # Try appending an integer
    with pytest.raises(PrologueError) as excinfo:
        block.append(123)
    assert "Entry must be a string or Block, not int" in str(excinfo.value)
    # Try appending a boolean
    with pytest.raises(PrologueError) as excinfo:
        block.append(True)
    assert "Entry must be a string or Block, not bool" in str(excinfo.value)
