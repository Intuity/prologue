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

class Block:
    """ Represents a block of lines between opening and closing delimiters """

    def __init__(self, parent):
        """ Initialise a block with a directive. """
        self.parent  = parent
        self.content = []

    def append(self, entry):
        """ Append either a new line of text or a nested Block instance.

        Args:
            entry: The line of text or nested Block
        """
        if not isinstance(entry, str) and not isinstance(entry, Block):
            raise PrologueError(
                f"Entry must be a string or Block, not {type(entry).__name__}"
            )
        self.content.append(entry)

    def evaluate(self, context):
        """ Evaluate the block and stream complete lines back to Prologue.

        Args:
            context: Context object at the point of evaluation

        Yields: A line of text at a time
        """
        from .directives.base import Directive
        for entry in self.content:
            if (
                (    isinstance(entry, Directive) and entry.yields            ) or
                (not isinstance(entry, Directive) and isinstance(entry, Block))
            ):
                yield from entry.evaluate(context)
            elif isinstance(entry, Directive):
                entry.evaluate(context)
            else:
                yield entry

    @property
    def stack(self):
        """ Returns the full stack of nodes including this one. """
        baseline = self.parent.stack if self.parent else []
        return baseline + [self]
