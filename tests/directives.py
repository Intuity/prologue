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

from unittest.mock import MagicMock, call

import pytest

from prologue.directives import register_prime_directives
from prologue.directives.conditional import Conditional
from prologue.directives.define import Define, Undefine
from prologue.directives.for_loop import ForLoop
from prologue.directives.include import Include, Import
from prologue.directives.message import Message

def test_directives_prime(mocker):
    """ Check that prime directives are registered correctly """
    pro = MagicMock()
    register_prime_directives(pro)
    pro.register_directive.assert_has_calls([
        call(Message),
        call(Define), call(Undefine),
        call(Conditional), call(ForLoop),
        call(Include), call(Import),
    ])
