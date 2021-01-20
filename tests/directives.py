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

from random import randint
from unittest.mock import MagicMock, call

import pytest

from prologue.directives import register_prime_directives
from prologue.directives.base import Directive
from prologue.directives.conditional import Conditional
from prologue.directives.define import Define, Undefine
from prologue.directives.for_loop import ForLoop
from prologue.directives.include import Include, Import
from prologue.directives.message import Message

def test_directive_prime(mocker):
    """ Check that prime directives are registered correctly """
    pro = MagicMock()
    register_prime_directives(pro)
    pro.register_directive.assert_has_calls([
        call(Message),
        call(Define), call(Undefine),
        call(Conditional), call(ForLoop),
        call(Include), call(Import),
    ])

def test_directive_uuid():
    """ Check that each directive instance is issued a unique identifier """
    # Reset UUID to a random starting point
    start_point    = randint(0, 1000)
    Directive.UUID = start_point
    # Construct ten different directives
    dir_insts = [Directive(None) for _x in range(10)]
    # Check UUIDs issued correctly
    for idx, dirx in enumerate(dir_insts):
        assert dirx.uuid == (start_point + idx)

def test_directive_split_args():
    """ Test splitting arguments paying attention to quotes """
    dirx = Directive(None)
    # Try basic space separation
    parts = dirx.split_args("AbC eFGhi 1234 X y")
    assert parts == ["AbC", "eFGhi", "1234", "X", "y"]
    # Try with double quotes around an argument
    parts = dirx.split_args('AbcD "hello world" X y 123')
    assert parts == ["AbcD", "hello world", "X", "y", "123"]
    # Try with single quotes around an argument
    parts = dirx.split_args("True False 'goodbye now' 4321")
    assert parts == ["True", "False", "goodbye now", "4321"]
    # Try with mixed quotes
    parts = dirx.split_args('Banana apple "hello \'world how\' are you?" 4321')
    assert parts == ["Banana", "apple", "hello 'world how' are you?", "4321"]

def test_directive_count_args():
    """ Test counting arguments paying attention to quotes """
    dirx = Directive(None)
    # Try basic space separation
    assert dirx.count_args("AbC eFGhi 1234 X y") == 5
    # Try with double quotes around an argument
    assert dirx.count_args('AbcD "hello world" X y 123') == 5
    # Try with single quotes around an argument
    assert dirx.count_args("True False 'goodbye now' 4321") == 4
    # Try with mixed quotes
    assert dirx.count_args('Banana apple "hello \'world how\' are you?" 4321') == 4

def test_directive_get_args():
    """ Test accessing a particular argument paying attention to quotes """
    dirx = Directive(None)
    # Try basic space separation
    assert dirx.get_arg("AbC eFGhi 1234 X y", 2) == "1234"
    # Try with double quotes around an argument
    assert dirx.get_arg('AbcD "hello world" X y 123', 1) == "hello world"
    # Try with single quotes around an argument
    assert dirx.get_arg("True False 'goodbye now' 4321", 0) == "True"
    # Try with mixed quotes
    assert dirx.count_args('Banana apple "hello \'world how\' are you?" 4321') == 4
