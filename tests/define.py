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
from prologue.directives.define import Define

from .common import random_str

def test_define_boolean():
    """ Test defining a variable without a value """
    for _x in range(100):
        define = Define.directive(None)
        # Check initial state
        assert define.name  == None
        assert define.value == None
        # Invoke with a random define name
        def_name = random_str(5, 10)
        define.invoke("define", def_name)
        assert define.name  == def_name
        assert define.value == True
        # Evaluate the define
        ctx = MagicMock()
        define.evaluate(ctx)
        ctx.set_define.assert_has_calls([call(def_name, True, check=True)])

def test_define_ascii():
    """ Test defining a variable with an ASCII value """
    for _x in range(100):
        define = Define.directive(None)
        # Check initial state
        assert define.name  == None
        assert define.value == None
        # Invoke with a random define name
        def_name = random_str(5, 10)
        def_val  = random_str(5, 10)
        define.invoke("define", f"{def_name} {def_val}")
        assert define.name  == def_name
        assert define.value == def_val
        # Evaluate the define
        ctx = MagicMock()
        define.evaluate(ctx)
        ctx.set_define.assert_has_calls([call(def_name, def_val, check=True)])

def test_define_integer():
    """ Test defining a variable with an integer value """
    for _x in range(100):
        define = Define.directive(None)
        # Check initial state
        assert define.name  == None
        assert define.value == None
        # Invoke with a random define name
        # NOTE: All defines are strings - numeric evaluation occurs later
        def_name = random_str(5, 10)
        def_val  = randint(0, 10000)
        define.invoke("define", f"{def_name} {def_val}")
        assert define.name  == def_name
        assert define.value == str(def_val)
        # Evaluate the define
        ctx = MagicMock()
        define.evaluate(ctx)
        ctx.set_define.assert_has_calls([call(def_name, str(def_val), check=True)])

def test_define_clash():
    """ Try defining a value that already exists """
    for _x in range(100):
        define = Define.directive(None)
        # Check initial state
        assert define.name  == None
        assert define.value == None
        # Invoke with a random define name
        # NOTE: All defines are strings - numeric evaluation occurs later
        def_name = random_str(5, 10)
        def_val  = randint(0, 10000)
        define.invoke("define", f"{def_name} {def_val}")
        assert define.name  == def_name
        assert define.value == str(def_val)
        # Evaluate the define
        ctx = MagicMock()
        define.evaluate(ctx)
        ctx.set_define.assert_has_calls([call(def_name, str(def_val), check=True)])

def test_define_bad_tag():
    """ Try defining a value with a bad tag """
    for _x in range(100):
        define = Define.directive(None)
        # Check initial state
        assert define.name  == None
        assert define.value == None
        # Invoke with a random define name
        bad_tag = random_str(5, 10, avoid=["define"])
        with pytest.raises(PrologueError) as excinfo:
            define.invoke(bad_tag, f"{random_str(5, 10)} {random_str(5, 10)}")
        assert f"Define invoked with '{bad_tag}'"
        assert define.name  == None
        assert define.value == None

def test_define_bad_form():
    """ Try defining a value with no arguments """
    define = Define.directive(None)
    # Check initial state
    assert define.name  == None
    assert define.value == None
    # Invoke with a random define name
    with pytest.raises(PrologueError) as excinfo:
        define.invoke("define", "")
    assert "Invalid form used for #define" == str(excinfo.value)
    assert define.name  == None
    assert define.value == None
