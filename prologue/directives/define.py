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

    def __init__(self, parent):
        super().__init__(parent)
        self.name  = None
        self.value = None

    def invoke(self, tag, arguments):
        """ Define a new variable in the context object.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity check
        num_args = self.count_args(arguments)
        if num_args not in (1, 2):
            raise PrologueError(f"Invalid form used for #define {arguments}")
        # Everything before the first space is taken as the variable name
        # NOTE: If no value is provided, it defaults to 'True'
        self.name  = self.get_arg(arguments, 0)
        self.value = self.get_arg(arguments, 1).strip() if num_args == 2 else True

    def evaluate(self, context):
        """ Define a variable.

        Args:
            context: The context object at the point of evaluation
        """
        # Sanity check for collision
        if context.has_define(self.name):
            raise PrologueError(
                f"Variable already defined for '{self.name}' with value " +
                str(context.get_define(self.name))
            )
        # Define the variable
        context.set_define(self.name, self.value)

@directive("undef")
class Undefine(LineDirective):
    """ Undefined a variable from the current context """

    def __init__(self, parent):
        super().__init__(parent)
        self.name = None

    def invoke(self, tag, arguments):
        """ Undefine an existing variable from the context object.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity check
        if self.count_args(arguments) != 1:
            raise PrologueError(f"Invalid form used for #undef {arguments}")
        # Everything before the first space is taken as the variable name
        self.name = self.get_arg(arguments, 0)

    def evaluate(self, context):
        """ Undefine a variable.

        Args:
            context: The context object at the point of evaluation
        """
        # Sanity check for collision
        if not context.has_define(self.name):
            raise PrologueError(f"No variable defined for '{self.name}'")
        # Undefine the variable
        context.clear_define(self.name)
