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
from prologue.directives.include import Include

from .common import random_str

def test_include():
    """ Include a file by name, check for request to the preprocessor """
    for _x in range(100):
        dummy_cb = MagicMock()
        inc      = Include.directive(None, callback=dummy_cb)
        # Check initial state
        assert inc.filename == None
        # Invoke with a random file name
        inc_file = random_str(10, 20)
        inc.invoke("include", inc_file)
        assert inc.filename == inc_file
        # Test evaluation
        lines = [random_str(30, 50, spaces=True) for _x in range(randint(5, 10))]
        ctx   = MagicMock()
        ctx.pro.evaluate_inner.side_effect = [iter(lines)]
        result = [x for x in inc.evaluate(ctx)]
        ctx.pro.evaluate_inner.assert_has_calls([call(
            inc_file, context=ctx, callback=dummy_cb,
        )])
        assert result == lines

def test_include_bad_tag():
    """ Try invoking a #include directive with a bad tag name """
    for _x in range(100):
        inc = Include.directive(None)
        # Check initial state
        assert inc.filename == None
        # Invoke with a bad tag name
        bad_tag = random_str(5, 10, avoid=["include"])
        with pytest.raises(PrologueError) as excinfo:
            inc.invoke(bad_tag, random_str(10, 20))
        assert f"Include invoked with '{bad_tag}'" in str(excinfo.value)
        assert inc.filename == None

def test_include_bad_form():
    """ Use a bad number of arguments to invoke #include """
    for _x in range(100):
        inc = Include.directive(None)
        # Check initial state
        assert inc.filename == None
        # Invoke with a bad number of arguments
        zero_args = choice((True, False))
        bad_args  = (
            "" if zero_args else " ".join([random_str(5, 10) for _x in range(randint(2, 10))])
        )
        with pytest.raises(PrologueError) as excinfo:
            inc.invoke("include", bad_args)
        assert f"Invalid form used for #include {bad_args}" in str(excinfo.value)
        assert inc.filename == None
