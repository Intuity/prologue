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
from prologue.directives.define import Undefine

from .common import random_str

def test_undefine():
    """ Test undefining a value """
    for _x in range(100):
        undef = Undefine.directive(None)
        # Check initial state
        assert undef.name == None
        # Invoke with a random define name
        def_name = random_str(5, 10)
        undef.invoke("undef", def_name)
        assert undef.name == def_name
        # Evaluate the define
        ctx = MagicMock()
        ctx.has_define.side_effect = [True]
        undef.evaluate(ctx)
        ctx.clear_define.assert_has_calls([call(def_name)])

def test_undefine_bad_variable():
    """ Check that a non-existent variable can't be undefined """
    for _x in range(100):
        undef = Undefine.directive(None)
        # Check initial state
        assert undef.name == None
        # Invoke with a random define name
        def_name = random_str(5, 10)
        undef.invoke("undef", def_name)
        assert undef.name == def_name
        # Evaluate the define
        ctx = MagicMock()
        undef.evaluate(ctx)
        # Check clear define was called
        assert ctx.clear_define.called

def test_undefine_bad_tag():
    """ Check that a bad tag is flagged """
    for _x in range(100):
        undef = Undefine.directive(None)
        # Check initial state
        assert undef.name == None
        # Invoke with a random tag name
        bad_tag = random_str(5, 10, avoid=["undef"])
        with pytest.raises(PrologueError) as excinfo:
            undef.invoke(bad_tag, random_str(5, 10))
        assert f"Undefine invoked with '{bad_tag}'" in str(excinfo.value)

def test_undefine_bad_form():
    """ Try invoking undefine with a bad number of arguments """
    for _x in range(100):
        undef = Undefine.directive(None)
        # Check initial state
        assert undef.name == None
        # Invoke with a random tag name
        zero_args = choice((True, False))
        bad_args  = (
            "" if zero_args else " ".join([random_str(5, 10) for _x in range(randint(2, 10))])
        )
        with pytest.raises(PrologueError) as excinfo:
            undef.invoke("undef", bad_args)
        assert f"Invalid form used for #undef {bad_args}" in str(excinfo.value)
