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
from .registry import Registry

class Prologue(object):
    """ Top-level of the preprocessor """

    def __init__(self, delimiter="#", shared_delimiter=False):
        """ Initialise the preprocessor.

        Args:
            delimiter       : Specify the character to use as the delimiter
                              (default: '#')
            shared_delimiter: Delimiter is also used to signify a comment
                              (default: False)
        """
        # Store attributes
        self.delimiter        = delimiter
        self.shared_delimiter = shared_delimiter
        # Create a registry instance
        self.registry = Registry()

    # ==========================================================================
    # Property Setters/Getters
    # ==========================================================================

    @property
    def delimiter(self): return self.__delimiter

    @delimiter.setter
    def delimiter(self, val):
        # Check delimiter
        if len(val.strip()) == 0:
            raise PrologueError("Delimiter should be at least one character")
        elif len(val.replace(" ", "")) != len(val):
            raise PrologueError("Delimiter should not contain whitespace")
        # Set delimiter
        self.__delimiter = val

    @property
    def shared_delimiter(self): return self.__shared_delimiter

    @shared_delimiter.setter
    def shared_delimiter(self, val):
        # Check value is True or False
        if not isinstance(val, bool):
            raise PrologueError("Shared delimiter should be True or False")
        # Set value
        self.__shared_delimiter = val

    # ==========================================================================
    # Registry Passthroughs
    # ==========================================================================

    def add_file(self, path):
        """ Add a file to the registry.

        Args:
            path: Path to add
        """
        self.registry.add_file(path)

    def add_folder(self, path, search_for=None, recursive=False):
        """ Add a folder to the registry, see Registry.add_folder for more info.

        Args:
            path      : Path to the root folder to add
            search_for: Provide a file extension to search for
            recursive : Whether to search recursively in this folder
        """
        self.registry.add_folder(path, search_for=search_for, recursive=recursive)

