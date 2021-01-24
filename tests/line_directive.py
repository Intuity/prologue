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
from prologue.directives.base import LineDirective

from .common import random_str

def test_line_directive():
    """ Test the base line directive class """
    parent    = {}
    yield_val = choice((True, False))
    line_dir  = LineDirective(parent=parent, yields=yield_val)
    with pytest.raises(PrologueError) as excinfo:
        line_dir.invoke(random_str(5, 10), random_str(10, 20))
    assert "Must provide implementation of 'invoke'" == str(excinfo.value)
