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
from prologue.context import Context
from prologue.registry import RegistryFile

from .common import random_str

def test_context_construction():
    """ Test creation of a context object """
    pro    = MagicMock()
    parent = MagicMock()
    ctx    = Context(pro, parent=parent)
    assert ctx.pro    == pro
    assert ctx.parent == parent
    parent.defines.side_effect = [{}]
    assert len(ctx.defines.keys()) == 0

def test_context_inherit_defines():
    """ Test that values defined in the root are passed down correctly """
    root    = Context(None)
    child_a = Context(None, parent=root)
    child_b = Context(None, parent=child_a)
    # Check that the root is consistent
    assert root.root    == root
    assert child_a.root == root
    assert child_b.root == root
    # Setup some basic defines values
    root_defs = {}
    for _x in range(10): root_defs[random_str(5, 10)] = random_str(5, 10)
    child_a_defs = {}
    for _x in range(10): child_a_defs[random_str(5, 10)] = random_str(5, 10)
    child_b_defs = {}
    for _x in range(10): child_b_defs[random_str(5, 10)] = random_str(5, 10)
    for key, val in root_defs.items()   : root.set_define(key, val)
    for key, val in child_a_defs.items(): child_a.set_define(key, val)
    for key, val in child_b_defs.items(): child_b.set_define(key, val)
    # Check that defines are inherited correctly
    assert root.defines    == root_defs
    assert child_a.defines == { **root_defs, **child_a_defs }
    assert child_b.defines == { **root_defs, **child_a_defs, **child_b_defs }

def test_context_inherit_stack_and_trace(mocker):
    """ Test that the stack and trace are always held by the root """
    root    = Context(None)
    child_a = Context(None, parent=root)
    child_b = Context(None, parent=child_a)
    # Push a stack entry to each layer
    # NOTE: First we patch RegistryFile's __init__ routine to avoid path check
    mocker.patch.object(RegistryFile, "__init__", lambda x, z: None)
    root_node    = RegistryFile(random_str(30, 50))
    child_a_node = RegistryFile(random_str(30, 50))
    child_b_node = RegistryFile(random_str(30, 50))
    root.stack_push(root_node)
    child_a.stack_push(child_a_node)
    child_b.stack_push(child_b_node)
    # Check the stack (at all levels)
    assert root.trace    == [root_node, child_a_node, child_b_node]
    assert child_a.trace == [root_node, child_a_node, child_b_node]
    assert child_b.trace == [root_node, child_a_node, child_b_node]
    # Check that the trace is currently the same set
    assert root.trace    == [root_node, child_a_node, child_b_node]
    assert child_a.trace == [root_node, child_a_node, child_b_node]
    assert child_b.trace == [root_node, child_a_node, child_b_node]
    # Try popping from stack at different levels
    assert choice((root, child_a, child_b)).stack_pop() == child_b_node
    assert choice((root, child_a, child_b)).stack_top() == child_a_node
    assert choice((root, child_a, child_b)).stack_pop() == child_a_node
    assert choice((root, child_a, child_b)).stack_top() == root_node
    assert choice((root, child_a, child_b)).stack_pop() == root_node
    assert choice((root, child_a, child_b)).stack_top() == None
    # Check stack is empty
    assert root.stack    == []
    assert child_a.stack == []
    assert child_b.stack == []
    # Check that the trace is unchanged
    assert root.trace    == [root_node, child_a_node, child_b_node]
    assert child_a.trace == [root_node, child_a_node, child_b_node]
    assert child_b.trace == [root_node, child_a_node, child_b_node]

def test_context_bad_push():
    """ Try pushing a non-RegistryFile object onto the stack """
    ctx = Context(None)
    for obj in [
        choice((True, False)), randint(0, 10000), random_str(5, 10),
        random_str(30, 50, spaces=True), {}, [], Context(None),
    ]:
        with pytest.raises(PrologueError) as excinfo:
            ctx.stack_push(obj)
        assert f"Trying to push {obj} to stack - must be a RegistryFile" == str(excinfo.value)

def test_context_bad_pop(mocker):
    """ Try popping from an empty stack """
    mocker.patch.object(RegistryFile, "__init__", lambda x, z: None)
    ctx = Context(None)
    for _x in range(100):
        for _y in range(randint(1, 10)):
            ctx.stack_push(RegistryFile(random_str(5, 10)))
        while ctx.stack_top() != None: ctx.stack_pop()
        with pytest.raises(PrologueError) as excinfo:
            ctx.stack_pop()
        assert "Trying to pop file from empty stack" == str(excinfo.value)

def test_context_stack_trace_consistency(mocker):
    """ Make random pushes and pops from stack and check consistency """
    mocker.patch.object(RegistryFile, "__init__", lambda x, z: None)
    ctx   = Context(None)
    state = []
    trace = []
    for _x in range(100):
        # Perform random stack pushes
        for _y in range(randint(1, 10)):
            state.append(RegistryFile(random_str(5, 10)))
            trace.append(state[-1])
            ctx.stack_push(state[-1])
            assert ctx.stack       == state
            assert ctx.stack_top() == state[-1]
        # Perform random stack pops
        for _y in range(randint(1, 10)):
            if ctx.stack_top() == None:
                assert len(state) == 0
                break
            assert ctx.stack_top() == state[-1]
            assert ctx.stack_pop() == state[-1]
            state.pop()
        # Check the final stack state
        assert ctx.stack == state
        assert ctx.trace == trace

def test_context_define_consistency():
    """ Check consistency for defining/undefining values """
    ctx   = Context(None)
    state = {}
    for _x in range(1000):
        # Define some random values
        for _y in range(randint(1, 10)):
            key        = random_str(5, 10, avoid=list(state.keys()))
            val        = random_str(5, 10)
            state[key] = val
            ctx.set_define(key, val)
            assert ctx.has_define(key)
            assert ctx.get_define(key) == val
        # Check a random selection of values
        for _y in range(1, 10):
            if len(state.keys()) == 0: break
            key = choice(list(state.keys()))
            assert ctx.has_define(key)
            assert ctx.get_define(key) == state[key]
        # Undefine a random selection of values
        for _y in range(1, 10):
            if len(state.keys()) == 0: break
            key = choice(list(state.keys()))
            assert ctx.has_define(key)
            ctx.clear_define(key)
            assert not ctx.has_define(key)
            with pytest.raises(PrologueError) as excinfo:
                ctx.get_define(key)
            assert f"No value has been defined for key '{key}'" == str(excinfo.value)
            del state[key]
    # Final state check
    for key, val in state.items():
        assert ctx.has_define(key)
        assert ctx.get_define(key) == val
        ctx.clear_define(key)
        assert not ctx.has_define(key)

def test_context_bad_define():
    """ Try defining and clearing a value with a bad key """
    ctx = Context(None)
    for _x in range(100):
        use_empty = choice((True, False))
        key_str   = "" if use_empty else f"{random_str(1, 5)} {random_str(1, 5)}"
        with pytest.raises(PrologueError) as excinfo:
            ctx.set_define(key_str, random_str(5, 10))
        assert (
            f"Key must not contain whitespace and must be at least one character "
            f"in length: '{key_str}'"
        ) == str(excinfo.value)
    for _x in range(100):
        use_key = random_str(5, 10)
        with pytest.raises(PrologueError) as excinfo:
            ctx.clear_define(use_key)
        assert f"No value has been defined for key '{use_key}'" == str(excinfo.value)

def test_context_redefine():
    """ Check that a warning message is produced when redefining a value """
    pro   = MagicMock()
    ctx   = Context(pro)
    state = {}
    for _x in range(100):
        key        = random_str(5, 10)
        val        = random_str(5, 10)
        state[key] = val
        ctx.set_define(key, val)
    for _x in range(100):
        use_key = choice(list(state.keys()))
        # Check the existing value
        assert ctx.has_define(use_key)
        assert ctx.get_define(use_key) == state[use_key]
        # Choose new state
        new_val = random_str(5, 10)
        en_warn = choice((True, False))
        # Redefine a value
        ctx.set_define(use_key, new_val, warning=en_warn)
        # Check that value has been overwritten
        assert ctx.has_define(use_key)
        assert ctx.get_define(use_key) == new_val
        state[use_key] = new_val
        # Check if the warning was triggered
        if en_warn:
            assert pro.warning_message.called
            pro.warning_message.assert_has_calls([call(
                f"Value already defined for key {use_key}",
                { "key": use_key, "value": new_val },
            )])
        else:
            assert not pro.warning_message.called
        # Reset the mock for the next pass
        pro.reset_mock()
