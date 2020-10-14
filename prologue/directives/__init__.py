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

from .logical import if_directive
from .message import info_directive, warn_directive, error_directive

def register_prime_directives(pro):
    """ Register prime directives onto an instance of Prologue.

    Args:
        pro: Pointer to Prologue instance
    """
    # Register message directives
    pro.register_directive(info_directive)
    pro.register_directive(warn_directive)
    pro.register_directive(error_directive)
    # Register logical directives
    pro.register_directive(if_directive)