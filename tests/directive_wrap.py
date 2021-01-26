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

from prologue.common import PrologueError
from prologue.directives.common import DirectiveWrap, directive
from prologue.directives.base import BlockDirective, LineDirective, Directive

from .common import random_str

def test_directive_wrap():
    """ Test wrapping a directive """
    class RootDirx(Directive): pass
    class BlockDirx(BlockDirective): pass
    class LineDirx(LineDirective): pass
    for _i in range(100):
        # Choose a directive and generate tags
        dirx       = choice((RootDirx, BlockDirx, LineDirx))
        opening    = [random_str(5, 10) for _x in range(randint(1, 10))]
        transition = [random_str(5, 10) for _x in range(randint(1, 10))] if (dirx == BlockDirx) else None
        closing    = [random_str(5, 10) for _x in range(randint(1, 10))] if (dirx == BlockDirx) else None
        # Wrap the directive
        print(f"Trying {dirx}")
        wrapped = DirectiveWrap(dirx, opening, closing=closing, transition=transition)
        assert wrapped.directive  == dirx
        assert wrapped.opening    == tuple(opening)
        assert wrapped.closing    == (tuple(closing) if closing else tuple())
        assert wrapped.transition == (tuple(transition) if transition else tuple())
        # Check all tags
        assert wrapped.tags == (
            tuple(opening) + (tuple(transition) if transition else tuple()) +
            (tuple(closing) if closing else tuple())
        )
        # Check whether block and line directives are correctly identified
        assert wrapped.is_block == (dirx == BlockDirx)
        assert wrapped.is_line  == (dirx == LineDirx)
        # Test the opening tags
        for _x in range(100):
            if choice((True, False)):
                assert wrapped.is_opening(choice(opening))
            elif (dirx == BlockDirective) and choice((True, False)):
                assert not wrapped.is_opening(choice(closing + transition))
            else:
                rand_tag = random_str(5, 10, avoid=(
                    opening + (closing if closing else []) +
                    (transition if transition else [])
                ))
                with pytest.raises(PrologueError) as excinfo:
                    wrapped.is_opening(rand_tag)
                assert f"Tag is not known by directive: {rand_tag}" == str(excinfo.value)
        # Test the transition tags
        for _x in range(100):
            if (dirx == BlockDirective) and choice((True, False)):
                assert wrapped.is_transition(choice(transition))
            elif (dirx == BlockDirective) and choice((True, False)):
                assert not wrapped.is_transition(choice(opening + closing))
            else:
                rand_tag = random_str(5, 10, avoid=(
                    opening + (closing if closing else []) +
                    (transition if transition else [])
                ))
                with pytest.raises(PrologueError) as excinfo:
                    wrapped.is_transition(rand_tag)
                assert f"Tag is not known by directive: {rand_tag}" == str(excinfo.value)
        # Test the closing tags
        for _x in range(100):
            if (dirx == BlockDirective) and choice((True, False)):
                assert wrapped.is_closing(choice(closing))
            elif (dirx == BlockDirective) and choice((True, False)):
                assert not wrapped.is_closing(choice(opening + transition))
            else:
                rand_tag = random_str(5, 10, avoid=(
                    opening + (closing if closing else []) +
                    (transition if transition else [])
                ))
                with pytest.raises(PrologueError) as excinfo:
                    wrapped.is_closing(rand_tag)
                assert f"Tag is not known by directive: {rand_tag}" == str(excinfo.value)

def test_directive_wrap_bad():
    """ Try misusing the DirectiveWrap class """
    class DummyA: pass
    class DummyB(str): pass
    class DummyC(list): pass
    class DummyD(dict): pass
    for _i in range(100):
        # Check for a bad directive type - expects a subclass of 'Directive'
        for obj in [DummyA, DummyB, DummyC, DummyD]:
            with pytest.raises(PrologueError) as excinfo:
                DirectiveWrap(obj, [random_str(5, 10) for _x in range(5)])
            assert f"Item is not a subclass of Directive: {obj}" == str(excinfo.value)
        # Check for bad opening tags
        dirx = choice((LineDirective, BlockDirective))
        with pytest.raises(PrologueError) as excinfo:
            DirectiveWrap(
                dirx, [], transition=[random_str(5, 10) for _x in range(5)],
                closing=[random_str(5, 10) for _x in range(5)],
            )
        assert "At least one opening tag must be specified" == str(excinfo.value)
        # Check for bad closing tags
        with pytest.raises(PrologueError) as excinfo:
            DirectiveWrap(
                BlockDirective, [random_str(5, 10) for _x in range(5)],
                transition=[random_str(5, 10) for _x in range(5)],
                closing=[],
            )
        assert "At least one closing tag must be specified" == str(excinfo.value)
        # Check for populated closing tags with a non-block directive
        dirx = choice((LineDirective, Directive))
        with pytest.raises(PrologueError) as excinfo:
            DirectiveWrap(
                dirx, [random_str(5, 10) for _x in range(5)],
                transition=[random_str(5, 10) for _x in range(5)],
                closing=[random_str(5, 10) for _x in range(5)],
            )
        assert "Only a block directive can have closing tags" == str(excinfo.value)
        # Check for populated transition tags with a non-block directive
        dirx = choice((LineDirective, Directive))
        with pytest.raises(PrologueError) as excinfo:
            DirectiveWrap(
                dirx, [random_str(5, 10) for _x in range(5)],
                transition=[random_str(5, 10) for _x in range(5)],
                closing=None,
            )
        assert "Only a block directive can have transition tags" == str(excinfo.value)
        # Test for bad tags
        with pytest.raises(PrologueError) as excinfo:
            tags = [random_str(30, 50, spaces=True) for _x in range(5)] if choice((True, False)) else ([""] * 5)
            DirectiveWrap(BlockDirective, tags, transition=tags, closing=tags,)
        assert (
            "Directive tag cannot contain spaces and must be at least one "
            "character in length"
        ) == str(excinfo.value)

def test_directive_decorator_bad():
    """ Test the @directive decorator on a non-BlockDirective/LineDirective """
    class DummyA(): pass
    class DummyB(str): pass
    class DummyC(dict): pass
    class DummyD(list): pass
    for obj in (DummyA, DummyB, DummyC, DummyD):
        with pytest.raises(PrologueError) as excinfo:
            directive(*[random_str(5, 10) for x in range(5)])(obj)
        assert "Directive must be a subclass of BlockDirective or LineDirective" == str(excinfo.value)

def test_directive_decorator_block():
    """ Test the @directive decorator on a block directive """
    bd = BlockDirective
    # Generate random opening, transition, and closing tags
    opening    = [random_str(5, 10) for _x in range(randint(1, 10))]
    transition = [random_str(5, 10) for _x in range(randint(0, 10))]
    closing    = [random_str(5, 10) for _x in range(randint(1, 10))]
    # Evaluate the directive
    wrapper = directive(*opening, closing=closing, transition=transition)
    d_wrap  = wrapper(bd)
    assert isinstance(d_wrap, DirectiveWrap)
    assert d_wrap.directive == bd
    assert bd.OPENING       == [x.lower() for x in opening]
    assert bd.TRANSITION    == [x.lower() for x in transition]
    assert bd.CLOSING       == [x.lower() for x in closing]

def test_directive_decorator_line():
    """ Test the @directive decorator on a line directive """
    ld = LineDirective
    # Generate random opening, transition, and closing tags
    opening = [random_str(5, 10) for _x in range(randint(1, 10))]
    # Evaluate the directive
    wrapper = directive(*opening)
    d_wrap  = wrapper(ld)
    assert isinstance(d_wrap, DirectiveWrap)
    assert d_wrap.directive == ld
    assert ld.OPENING       == [x.lower() for x in opening]
    assert ld.TRANSITION    == None
    assert ld.CLOSING       == None

def test_directive_decorator_block_bad():
    """ Test the @directive decorator on a block directive with bad setup """
    bd = BlockDirective
    # Try a directive with no opening tags
    with pytest.raises(PrologueError) as excinfo:
        directive()(bd)
    assert "At least one opening directive must be given" == str(excinfo.value)
    # Try a directive with no closing tags
    with pytest.raises(PrologueError) as excinfo:
        directive(*[random_str(5, 10) for _x in range(5)])(bd)
    assert "Closing tags must be specified for a block directive" == str(excinfo.value)

def test_directive_decorator_line_bad():
    """ Test the @directive decorator on a line directive with bad setup """
    ld = LineDirective
    # Try a directive with no opening tags
    with pytest.raises(PrologueError) as excinfo:
        directive()(ld)
    assert "At least one opening directive must be given" == str(excinfo.value)
    # Try a directive with transition tags
    with pytest.raises(PrologueError) as excinfo:
        directive(
            *[random_str(5, 10) for _x in range(5)],
            transition=[random_str(5, 10) for _x in range(5)],
        )(ld)
    assert "Closing or transition tags can only be used with a block directive" == str(excinfo.value)
    # Try a directive with closing tags
    with pytest.raises(PrologueError) as excinfo:
        directive(
            *[random_str(5, 10) for _x in range(5)],
            closing=[random_str(5, 10) for _x in range(5)],
        )(ld)
    assert "Closing or transition tags can only be used with a block directive" == str(excinfo.value)


