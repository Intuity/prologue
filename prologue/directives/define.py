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

from .base import LineDirective
from .common import directive
from ..common import PrologueError

@directive("define")
class Define(LineDirective):
    """ Defines a variable in the current context """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, src_file=src_file, src_line=src_line, callback=callback,
        )
        self.name  = None
        self.value = None

    def invoke(self, tag, arguments):
        """ Define a new variable in the context object.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity checks
        if tag != "define":
            raise PrologueError(f"Define invoked with '{tag}'")
        # Test number of arguments
        # NOTE: At least one argument (the name) must be provided, but as an
        #       expression can be used in a define, there is no upper limit on
        #       arguments as counted by shlex
        num_args = self.count_args(arguments)
        if num_args < 1: raise PrologueError("Invalid form used for #define")
        # Everything before the first space is taken as the variable name, and
        # everything after the first space is the value
        self.name  = self.get_arg(arguments, 0)
        self.value = arguments[len(self.name)+1:].strip()
        # If no value is provided, it acts like a flag with value 'True'
        if len(self.value) == 0: self.value = True

    def evaluate(self, context):
        """ Define a variable.

        Args:
            context: The context object at the point of evaluation
        """
        context.set_define(self.name, self.value, check=True)

@directive("undef")
class Undefine(LineDirective):
    """ Undefined a variable from the current context """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, src_file=src_file, src_line=src_line, callback=callback,
        )
        self.name = None

    def invoke(self, tag, arguments):
        """ Undefine an existing variable from the context object.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity check
        if tag != "undef":
            raise PrologueError(f"Undefine invoked with '{tag}'")
        if self.count_args(arguments) != 1:
            raise PrologueError(f"Invalid form used for #undef {arguments}")
        # Everything before the first space is taken as the variable name
        self.name = self.get_arg(arguments, 0)

    def evaluate(self, context):
        """ Undefine a variable.

        Args:
            context: The context object at the point of evaluation
        """
        context.clear_define(self.name)
