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

import shlex

from ..common import PrologueError
from ..block import Block

class Directive(Block):
    UUID = 0

    def __init__(
        self, parent, yields=True, src_file=None, src_line=0, callback=None,
    ):
        """ Initialise the directive.

        Args:
            parent  : The parent block
            yields  : Whether the directive yields content
            src_file: Source file
            src_line: Source line number
            callback: External callback routine to expose parse state
        """
        super().__init__(parent)
        self.__uuid     = BlockDirective.issue_uuid()
        self.__yields   = yields
        self.__source   = (src_file, src_line)
        self.__callback = callback

    @property
    def yields(self): return self.__yields

    @property
    def uuid(self): return self.__uuid

    @property
    def source(self): return self.__source

    @property
    def callback(self): return self.__callback

    @classmethod
    def issue_uuid(self):
        issue = Directive.UUID
        Directive.UUID += 1
        return issue

    def split_args(self, args):
        """ Split an argument string into parts, paying attention to quotes.

        Args:
            args: The string to split

        Returns: Array of sections
        """
        return shlex.split(args)

    def count_args(self, args):
        """ Count the number of arguments found, paying attention to quotes.

        Args:
            args: The string to split

        Returns: Number of arguments found
        """
        return len(self.split_args(args))

    def get_arg(self, args, index, default=None):
        """ Get the Nth argument from a string paying attention to quotes.

        Args:
            args   : The string to parse
            index  : The section to extract
            default: The default value to return if index out of range
        """
        parts = self.split_args(args)
        return parts[index] if index < len(parts) else default

class BlockDirective(Directive):
    """
    A block directive contains lines and other directives for which evaluation
    is postponed until the block is closed. Blocks must have an opening and
    closing tag, but can also be split into multiple sections using transitions.
    """

    def __init__(
        self, parent, yields=True, src_file=None, src_line=0, callback=None
    ):
        """ Initialise the block directive.

        Args:
            parent  : The parent block
            yields  : Whether the directive yields content (defaults to True for block)
            src_file: Source file
            src_line: Source line number
            callback: External callback routine to expose parse state
        """
        super().__init__(parent, yields, src_file, src_line, callback)
        self.__opened = False
        self.__closed = False

    @property
    def opened(self): return self.__opened

    @property
    def closed(self): return self.__closed

    def open(self, tag, arguments):
        """ Called once for the opening directive of the block.

        Args:
            tag      : The tag that opens the directive
            arguments: Argument string following the directive
        """
        if self.__opened:
            raise PrologueError("Multiple opening statements for block detected")
        self.__opened = True

    def transition(self, tag, arguments):
        """ Called for every transition between different sections of the directive.

        Args:
            tag      : The tag that opens the section
            arguments: Argument string following the directive
        """
        if not self.__opened:
            raise PrologueError(f"Transition '{tag}' used before opening directive")
        elif self.__closed:
            raise PrologueError(f"Transition '{tag}' used after closing directive")

    def close(self, tag, arguments):
        """ Called once to close the directive.

        Args:
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

    def __init__(
        self, parent, yields=False, src_file=None, src_line=0, callback=None,
    ):
        """ Initialise the block directive.

        Args:
            parent  : The parent block
            yields  : Whether the directive yields content (defaults to False for line)
            src_file: Source file
            src_line: Source line number
            callback: External callback routine to expose parse state
        """
        super().__init__(parent, yields, src_file, src_line, callback)

    def invoke(self, tag, arguments):
        """ Called once to setup the directive.

        Args:
            tag      : The tag that opens the directive
            arguments: Argument string following the directive
        """
        raise PrologueError("Must provide implementation of 'invoke'")
