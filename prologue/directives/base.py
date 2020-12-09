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

from ..common import PrologueError
from ..block import Block

class Directive(Block):
    UUID = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.__uuid = BlockDirective.issue_uuid()

    @property
    def uuid(self):
        """ Return the UUID (meant to be immutable) """
        return self.__uuid

    @classmethod
    def issue_uuid(self):
        issue = Directive.UUID
        Directive.UUID += 1
        return issue

class BlockDirective(Directive):
    """
    A block directive contains lines and other directives for which evaluation
    is postponed until the block is closed. Blocks must have an opening and
    closing tag, but can also be split into multiple sections using transitions.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.__opened = False
        self.__closed = False

    @property
    def opened(self): return self.__opened

    @property
    def closed(self): return self.__closed

    def open(self, context, tag, arguments):
        """ Called once for the opening directive of the block.

        Args:
            context  : Context object carrying variable state
            tag      : The tag that opens the directive
            arguments: Argument string following the directive
        """
        if self.__opened:
            raise PrologueError("Multiple opening statements for block detected")
        self.__opened = True

    def transition(self, context, tag, arguments):
        """ Called for every transition between different sections of the directive.

        Args:
            context  : Context object carrying variable state
            tag      : The tag that opens the section
            arguments: Argument string following the directive
        """
        if not self.__opened:
            raise PrologueError(f"Transition '{tag}' used before opening directive")
        elif self.__closed:
            raise PrologueError(f"Transition '{tag}' used after closing directive")

    def close(self, context, tag, arguments):
        """ Called once to close the directive.

        Args:
            context  : Context object carrying variable state
            tag      : The tag that opens the directive
            arguments: Argument string following the directive
        """
        if self.__closed:
            raise PrologueError("Multiple closing statements for block detected")
        self.__closed = True

    def append(self, entry):
        """ Append a new line or nested block to the active block.

        Args:
            entry: The line or block to append.
        """
        # Sanity checks
        if not self.opened:
            raise PrologueError("Trying to append a line to an unopened directive")
        elif self.closed:
            raise PrologueError("Trying to append a line to a closed directive")
        # Call append on parent class
        super().append(entry)

class LineDirective(Directive):
    """
    A line directive performs a single action. Evaluation is only postponed if
    it is embedded within a block directive.
    """

    def invoke(self, context, tag, arguments):
        raise PrologueError("Must provide implementation of 'invoke'")
