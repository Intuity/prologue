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

from .base import BlockDirective
from ..block import Block
from .common import directive
from ..common import PrologueError

@directive(opening=["for"], closing=["endfor"])
class ForLoop(BlockDirective):
    """ Loop directive using FOR/ENDFOR """

    def __init__(self, parent):
        super().__init__(parent)
        self.loop = None

    def open(self, context, tag, arguments):
        super().open(context, tag, arguments)
        # Sanity checks
        if tag != "for":
            raise PrologueError(f"Loop opening invoked with '{tag}'")
        # Record the loop argument
        self.loop = arguments

    def close(self, context, tag, arguments):
        super().close(context, tag, arguments)
        # Sanity checks
        if tag != "endfor":
            raise PrologueError(f"Loop close invoked with '{tag}'")

    def evaluate(self):
        """ Repeats the embedded block as many times as required.

        Yields: A line of text at a time
        """
        # TODO: Evaluate the loop condition
        states = [1, 2, 3, 4, 5]
        # Repeatedly evaluate the embedded block
        for state in states:
            # TODO: Export the loop variable(s) into the context
            yield from super().evaluate()
