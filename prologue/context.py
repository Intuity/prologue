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

from .common import PrologueError

class Context(object):
    """ Keeps track of the parser's context """

    def __init__(self, pro, parent=None):
        """ Initialise the context

        Args:
            pro   : Pointer to the root Prologue instance
            parent: Pointer to the parent Context object prior to fork
        """
        self.pro     = pro
        self.defines = {}
        self.stack   = []
        self.parent  = parent

    # ==========================================================================
    # Defined Value Management
    # ==========================================================================

    def set_define(self, key, value):
        """ Define a value for a key, checks whether the key clashes.

        Args:
            key  : The key of the define
            value: The value of the define
        """
        # Check the key is sane
        if " " in key or len(key) == 0:
            raise PrologueError(
                f"Key must not contain whitespace and must be at least one "
                f"character in length: '{key}'"
            )
        # Warn about collision
        if key in self.defines:
            self.pro.warning_message(
                f"Value already defined for key {key}",
                { "key": key, "value": value },
            )
        # Store the define
        self.defines[key] = value

    def clear_define(self, key):
        """
        Remove a defined value from the context based on a key, an exception is
        raised if the key is unknown.

        Args:
            key: The key of the defined value
        """
        if key not in self.defines:
            raise PrologueError(f"No value has been defined for key '{key}'")
        del self.defines[key]

    def get_define(self, key):
        """ Return a value if the key is known, otherwise raise an exception.

        Args:
            key: The key of the defined value

        Returns: Value of the define
        """
        if key not in self.defines:
            raise PrologueError(f"No value has been defined for key '{key}'")
        return self.defines[key]

    # ==========================================================================
    # Forking and Joining
    # ==========================================================================

    def fork(self):
        """ Creates a copy of the context object allowing for delayed evaluation.

        Returns: Instance of Context with copied defines
        """
        # Create new the context instance
        new = Context(self.pro, parent=self)
        new.defines = { **self.defines }
        return new

    def join(self):
        """ Joins a child context object back into it's parent.

        Returns: Pointer to the parent context
        """
        if not self.parent:
            raise PrologueError("No parent configured for context object")
        for key, value in self.defines.items():
            self.parent.set_define(key, value)
        return self.parent