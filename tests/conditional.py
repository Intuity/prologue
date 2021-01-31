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
from prologue.directives.conditional import Conditional

from .common import random_str

def test_conditional_single():
    """ Check a conditional directive opens with 'if', closed with 'endif' """
    cond = Conditional.directive(None)
    # Check that initial state is correct
    assert not cond.opened and not cond.closed
    assert cond.if_section    == None
    assert cond.elif_sections == []
    assert cond.else_section  == None
    # Open with a valid statement
    cond.open("if", "a == b")
    assert cond.opened and not cond.closed
    assert cond.if_section    != None
    assert cond.if_section[0] == "if"
    assert cond.if_section[1] == "a == b"
    assert isinstance(cond.if_section[2], Block)
    assert cond.elif_sections == []
    assert cond.else_section  == None
    # Close the block
    cond.close("endif", "")
    assert cond.opened and cond.closed
    assert cond.if_section != None
    assert cond.if_section[0] == "if"
    assert cond.if_section[1] == "a == b"
    assert isinstance(cond.if_section[2], Block)
    assert cond.elif_sections == []
    assert cond.else_section  == None

def test_conditional_multiple():
    """ Check that multiple ELIF sections are supported """
    cond = Conditional.directive(None)
    # Open the conditional
    if_arg = random_str(5, 10)
    cond.open("if", if_arg)
    # Create multiple ELIF transitions
    elif_args = [random_str(5, 10) for _x in range(randint(2, 10))]
    for arg in elif_args: cond.transition("elif", arg)
    # Create final transition to ELSE
    else_arg = random_str(5, 10)
    cond.transition("else", else_arg)
    # Close the conditional
    cond.close("endif", "")
    # Check the contents
    assert cond.opened and cond.closed
    assert cond.if_section[0]      == "if"
    assert cond.if_section[1]      == if_arg
    assert len(cond.elif_sections) == len(elif_args)
    for elif_sect, elif_arg in zip(cond.elif_sections, elif_args):
        assert elif_sect[0] == "elif"
        assert elif_sect[1] == elif_arg
    assert cond.else_section[0] == "else"
    assert cond.else_section[1] == else_arg

def test_conditional_bad_open():
    """ Test opening a conditional with a random string """
    cond = Conditional.directive(None)
    for opening in (
        ["elif", "else", "endif"] +
        [random_str(1, 10, avoid=["if"]) for _x in range(10)]
    ):
        with pytest.raises(PrologueError) as excinfo:
            cond.open(opening, random_str(5, 15))
        assert f"Conditional opening invoked with '{opening}'" in str(excinfo.value)
        assert cond.if_section == None

def test_conditional_bad_transition():
    """ Test transition between blocks with a random string """
    cond = Conditional.directive(None)
    cond.open("if", random_str(5, 10))
    for transition in (
        ["if", "endif"] +
        [random_str(1, 10, ["elif", "else"]) for _x in range(10)]
    ):
        with pytest.raises(PrologueError) as excinfo:
            cond.transition(transition, random_str(5, 15))
        assert f"Conditional transition invoked with '{transition}'"
        assert len(cond.elif_sections) == 0

def test_conditional_bad_after_else():
    """ Test that transitions after 'else' is seen are flagged """
    cond = Conditional.directive(None)
    cond.open("if", random_str(5, 10))
    cond.transition("elif", random_str(5, 10))
    cond.transition("else", random_str(5, 10))
    elif_sects          = cond.elif_sections[:]
    e_tag, e_arg, e_blk = cond.else_section
    # Try a number of random transitions
    for _x in range(10):
        use_elif = choice((True, False))
        with pytest.raises(PrologueError) as excinfo:
            if use_elif:
                cond.transition("elif", random_str(5, 10))
            else:
                cond.transition("else", random_str(5, 10))
        # Sanity check result
        assert f"Transition '{'elif' if use_elif else 'else'}' detected after 'else' clause" in str(excinfo.value)
        assert cond.elif_sections   == elif_sects
        assert cond.else_section[0] == e_tag
        assert cond.else_section[1] == e_arg
        assert cond.else_section[2] == e_blk

def test_conditional_bad_close():
    """ Try closing the conditional without 'endif' """
    cond = Conditional.directive(None)
    cond.open("if", random_str(5, 10))
    cond.transition("elif", random_str(5, 10))
    cond.transition("else", random_str(5, 10))
    # Try a number of random closing statements
    for closing in (
        ["if", "elif", "else"] +
        [random_str(5, 10) for _x in range(randint(1, 10))]
    ):
        with pytest.raises(PrologueError) as excinfo:
            cond.close(closing, random_str(5, 10))
        assert f"Conditional close invoked with '{closing}'" in str(excinfo.value)
        assert not cond.closed

def gen_body(cond):
    """ Populates a random body into each section.

    Args:
        cond: Conditional instance

    Returns: The lines populated into the active section
    """
    lines = []
    for _x in range(randint(20, 30)):
        lines.append(random_str(20, 30))
        cond.append(lines[-1])
    return lines

def test_conditional_append():
    """ Append text to different sections of the conditional block """
    cond = Conditional.directive(None)
    # First populate the 'IF' opening section
    if_arg = random_str(5, 10)
    cond.open("if", if_arg)
    if_lines = gen_body(cond)
    # Now populate a number of 'ELIF' sections
    elif_args  = []
    elif_lines = []
    for _x in range(randint(1, 3)):
        elif_args.append(random_str(5, 10))
        cond.transition("elif", elif_args[-1])
        elif_lines.append(gen_body(cond))
    # Finally populate the 'ELSE' section
    else_arg = random_str(5, 10)
    cond.transition("else", else_arg)
    else_lines = gen_body(cond)
    # Close the conditional
    cond.close("endif", "")
    # Check the lines are stored correctly for 'IF'
    assert cond.if_section[0]         == "if"
    assert cond.if_section[1]         == if_arg
    assert cond.if_section[2].content == if_lines
    # Now check 'ELIF' sections
    assert len(elif_args) == len(elif_lines)
    assert len(elif_args) == len(cond.elif_sections)
    for arg, lines, sect in zip(elif_args, elif_lines, cond.elif_sections):
        assert sect[0]         == "elif"
        assert sect[1]         == arg
        assert sect[2].content == lines
    # Finally check 'ELSE' section
    assert cond.else_section[0]         == "else"
    assert cond.else_section[1]         == else_arg
    assert cond.else_section[2].content == else_lines


def test_conditional_append_unopened():
    """ Try appending lines to an unopened conditional """
    cond = Conditional.directive(None)
    with pytest.raises(PrologueError) as excinfo:
        cond.append("Hello 1234")
    assert "Trying to append a line to an unopened conditional" in str(excinfo.value)

def test_conditional_append_closed():
    """ Try appending lines to a closed conditional """
    cond = Conditional.directive(None)
    cond.open("if", random_str(5, 10))
    cond.close("endif", random_str(5, 10))
    with pytest.raises(PrologueError) as excinfo:
        cond.append("Hello 1234")
    assert "Trying to append a line to a closed conditional" in str(excinfo.value)

def test_conditional_evaluate(mocker):
    """ Check that evaluating a conditional returns the right contents """
    cond = Conditional.directive(None)
    # First populate the 'IF' opening section
    if_arg = random_str(5, 10)
    cond.open("if", if_arg)
    if_lines = gen_body(cond)
    # Now populate a number of 'ELIF' sections
    elif_args  = []
    elif_lines = []
    for _x in range(randint(1, 3)):
        elif_args.append(random_str(5, 10))
        cond.transition("elif", elif_args[-1])
        elif_lines.append(gen_body(cond))
    # Finally populate the 'ELSE' section
    else_arg = random_str(5, 10)
    cond.transition("else", else_arg)
    else_lines = gen_body(cond)
    # Close the conditional
    cond.close("endif", "")
    # Evaluate the 'IF' section
    ctx = MagicMock()
    ctx.evaluate.side_effect = [True] + ([False] * (len(elif_args) + 1))
    assert [x for x in cond.evaluate(ctx)] == if_lines
    ctx.evaluate.assert_has_calls([call(if_arg)])
    # Evaluate each 'ELIF' section in turn
    call_list = [call(if_arg)]
    for idx, (arg, lines) in enumerate(zip(elif_args, elif_lines)):
        ctx = MagicMock()
        ctx.evaluate.side_effect = (
            ([False] * (idx + 1)) + [True] + ([False] * (len(elif_lines) - idx))
        )
        assert [x for x in cond.evaluate(ctx)] == lines
        call_list.append(call(arg))
        ctx.evaluate.assert_has_calls(call_list)
    # Evaluate the 'ELSE' section
    ctx = MagicMock()
    ctx.evaluate.side_effect = ([False] * (len(elif_lines)+1)) + [True]
    assert [x for x in cond.evaluate(ctx)] == else_lines
    ctx.evaluate.assert_has_calls(call_list + [call(else_arg)])
