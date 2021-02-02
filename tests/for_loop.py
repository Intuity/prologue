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
from prologue.directives.for_loop import ForLoop

from .common import random_str

def test_for_loop_create():
    """ Test the opening and closing of a for loop block directive """
    loop = ForLoop.directive(None)
    # Check that initial state is correct
    assert not loop.opened and not loop.closed
    assert loop.loop == None
    # Open the loop, check it remembers the state
    open_arg = random_str(5, 10)
    loop.open("for", open_arg)
    assert loop.opened and not loop.closed
    assert loop.loop == open_arg
    # Close the loop, and check
    close_arg = random_str(5, 10)
    loop.close("endfor", close_arg)
    assert loop.opened and loop.closed
    assert loop.loop == open_arg

def test_for_loop_bad_open():
    """ Check that the loop cannot be opened with a bad tag """
    loop = ForLoop.directive(None)
    # Check the initial state
    assert not loop.opened and not loop.closed
    assert loop.loop == None
    # Try to open the loop with random strings
    for opening in (
        ["endfor"] +
        [random_str(5, 10, avoid=["for"]) for _x in range(randint(10, 20))]
    ):
        with pytest.raises(PrologueError) as excinfo:
            loop.open(opening, random_str(5, 10))
        assert f"Loop opening invoked with '{opening}'" in str(excinfo.value)
        assert not loop.opened and not loop.closed
        assert loop.loop == None

def test_for_loop_bad_close():
    """ Check that the loop cannot be closed with a bad tag """
    loop = ForLoop.directive(None)
    # Check the initial state
    assert not loop.opened and not loop.closed
    assert loop.loop == None
    # Open the loop
    open_arg = random_str(5, 10)
    loop.open("for", open_arg)
    assert loop.opened and not loop.closed
    assert loop.loop == open_arg
    # Try to open the loop with random strings
    for closing in (
        ["for"] +
        [random_str(5, 10, avoid=["endfor"]) for _x in range(randint(10, 20))]
    ):
        with pytest.raises(PrologueError) as excinfo:
            loop.close(closing, random_str(5, 10))
        assert f"Loop close invoked with '{closing}'" in str(excinfo.value)
        assert loop.opened and not loop.closed
        assert loop.loop == open_arg

def test_for_loop_transition():
    """ Test that using a transition with a for loop is rejected """
    loop = ForLoop.directive(None)
    # Check the initial state
    assert not loop.opened and not loop.closed
    assert loop.loop == None
    # Open the loop
    open_arg = random_str(5, 10)
    loop.open("for", open_arg)
    assert loop.opened and not loop.closed
    assert loop.loop == open_arg
    # Attempt to transition
    with pytest.raises(PrologueError) as excinfo:
        loop.transition(random_str(5, 10), random_str(5, 10))
    assert "For loop does not support transitions" in str(excinfo.value)

def test_for_loop_bad_condition():
    """ Check that a for loop cannot evaluate based on a bad condition """
    for _x in range(100):
        loop      = ForLoop.directive(None)
        loop_cond = " ".join([
            random_str(5, 10), random_str(1, 5, avoid=["in"]), random_str(5, 10)
        ])
        loop.open("for", loop_cond)
        loop.close("endfor", "")
        assert loop.opened and loop.closed
        with pytest.raises(PrologueError) as excinfo:
            lines = [x for x in loop.evaluate(None)]
        assert f"Incorrectly formed loop condition '{loop_cond}'" in str(excinfo.value)

def test_for_loop_evaluate():
    """ Test evaluation of a for loop """
    loop      = ForLoop.directive(None)
    loop_var  = random_str(5, 10)
    loop_rng  = random_str(5, 10)
    loop_cond = " ".join([loop_var, "in", loop_rng])
    loop.open("for", loop_cond)
    # Fill the loop with some random content
    lines = []
    for _x in range(randint(20, 30)):
        lines.append(random_str(30, 50))
        loop.append(lines[-1])
    # Close the loop and check state
    loop.close("endfor", "")
    assert loop.opened and loop.closed
    assert loop.loop == loop_cond
    # Try evaluating the loop with different numbers of repeats
    for num_rpt in range(1, 11):
        ctx = MagicMock()
        ctx.flatten.side_effect = [f"range({num_rpt})"]
        def echo(input_str): return input_str
        ctx.substitute.side_effect = echo
        result = [x for x in loop.evaluate(ctx)]
        assert result == (num_rpt * lines)
        ctx.flatten.assert_has_calls([call(loop_rng)])
        ctx.set_define.assert_has_calls([
            call(loop_var, x, warning=False) for x in range(num_rpt)
        ])
