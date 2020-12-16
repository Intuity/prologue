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

from .conditional import Conditional
from .define import Define, Undefine
from .for_loop import ForLoop
from .include import Include, Import
from .message import Message

def register_prime_directives(pro):
    """ Register prime directives onto an instance of Prologue.

    Args:
        pro: Pointer to Prologue instance
    """
    # Register message directives
    pro.register_directive(Message)
    # Variable define/undefine
    pro.register_directive(Define)
    pro.register_directive(Undefine)
    # Register logical directives
    pro.register_directive(Conditional)
    pro.register_directive(ForLoop)
    # Include/import directives
    pro.register_directive(Include)
    pro.register_directive(Import)
