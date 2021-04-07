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
from prologue.directives.include import Import

from .common import random_str

def test_import():
    """ Import a file by name, check for request to the preprocessor """
    for _x in range(100):
        dummy_cb = MagicMock()
        imp      = Import.directive(None, callback=dummy_cb)
        # Check initial state
        assert imp.filename == None
        # Invoke with a random file name
        imp_file = random_str(10, 20)
        imp.invoke("import", imp_file)
        assert imp.filename == imp_file
        # Test evaluation
        lines  = [random_str(30, 50, spaces=True) for _x in range(randint(5, 10))]
        ctx    = MagicMock()
        r_file = { "file": "my_file" }
        ctx.pro.registry.resolve.side_effect = [r_file]
        ctx.pro.evaluate_inner.side_effect = [iter(lines)]
        ctx.trace = []
        result    = [x for x in imp.evaluate(ctx)]
        ctx.pro.registry.resolve.assert_has_calls([call(imp_file)])
        ctx.pro.evaluate_inner.assert_has_calls([call(
            imp_file, context=ctx, callback=dummy_cb,
        )])
        assert result == lines

def test_import_duplicate():
    """ Check that a file won't be imported for a second time """
    for _x in range(100):
        imp = Import.directive(None)
        # Check initial state
        assert imp.filename == None
        # Invoke with a random file name
        imp_file = random_str(10, 20)
        imp.invoke("import", imp_file)
        assert imp.filename == imp_file
        # Test evaluation
        lines = [random_str(30, 50, spaces=True) for _x in range(randint(5, 10))]
        ctx   = MagicMock()
        r_file = { "file": "my_file" }
        ctx.pro.registry.resolve.side_effect = [r_file]
        ctx.pro.evaluate_inner.side_effect = [iter(lines)]
        ctx.trace = [r_file]
        result    = [x for x in imp.evaluate(ctx)]
        assert not ctx.pro.evaluate_inner.called
        assert result == []

def test_import_bad_tag():
    """ Try invoking a #import directive with a bad tag name """
    for _x in range(100):
        imp = Import.directive(None)
        # Check initial state
        assert imp.filename == None
        # Invoke with a bad tag name
        bad_tag = random_str(5, 10, avoid=["import"])
        with pytest.raises(PrologueError) as excinfo:
            imp.invoke(bad_tag, random_str(10, 20))
        assert f"Import invoked with '{bad_tag}'" in str(excinfo.value)
        assert imp.filename == None

def test_import_bad_form():
    """ Use a bad number of arguments to invoke #import """
    for _x in range(100):
        imp = Import.directive(None)
        # Check initial state
        assert imp.filename == None
        # Invoke with a bad number of arguments
        zero_args = choice((True, False))
        bad_args  = (
            "" if zero_args else " ".join([random_str(5, 10) for _x in range(randint(2, 10))])
        )
        with pytest.raises(PrologueError) as excinfo:
            imp.invoke("import", bad_args)
        assert f"Invalid form used for #import {bad_args}" in str(excinfo.value)
        assert imp.filename == None
