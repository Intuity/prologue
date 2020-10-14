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

from enum import IntEnum, auto

from ..common import PrologueError

class DirectiveType(IntEnum):
    """ Enumeration for directive types """
    LINE  = auto() # Single line directive (no 'end' required)
    BLOCK = auto() # Block directive (requires 'end')

class Directive(object):
    """ Decorator around a directive function """

    def __init__(self, function, tags, type):
        """ Initialise the wrapper

        Args:
            function: Function to wrap
            tags    : List of tags for registering the directive
            type    : Type of the directive (e.g. BLOCK or LINE)
        """
        # Check function
        if not callable(function):
            raise PrologueError(f"Function is not callable: {function}")
        # Check tags
        if not isinstance(tags, tuple) or len(tags) == 0:
            raise PrologueError("At least one directive tag must be specified")
        for tag in tags:
            if " " in tag or len(tag) == 0:
                raise PrologueError(
                    "Directive tag cannot contain spaces and must be at least "
                    "one character in length"
                )
        # Check type
        if type not in DirectiveType:
            raise PrologueError(f"Unknown directive type {type}")
        # Store arguments
        self.function = function
        self.tags     = tags
        self.type     = type

    def __call__(self, *args, **kwargs):
        yield from self.function(*args, **kwargs)

def block_directive(*tags):
    """ Decorator for a block directive

    Args:
        *tags: Accepts a list of tags to identify the directive
    """
    def wrapper(_func):
        return Directive(_func, tags, DirectiveType.BLOCK)
    return wrapper

def line_directive(*tags):
    """ Decorator for a line directive

    Args:
        *tags: Accepts a list of tags to identify the directive
    """
    def wrapper(_func):
        return Directive(_func, tags, DirectiveType.LINE)
    return wrapper
