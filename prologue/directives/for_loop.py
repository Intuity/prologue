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

import asteval

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

    def open(self, tag, arguments):
        # Sanity checks
        if tag != "for":
            raise PrologueError(f"Loop opening invoked with '{tag}'")
        # Only open loop after the sanity checks
        super().open(tag, arguments)
        # Record the loop argument
        self.loop = arguments

    def transition(self, tag, arguments):
        raise PrologueError("For loop does not support transitions")

    def close(self, tag, arguments):
        # Sanity checks
        if tag != "endfor":
            raise PrologueError(f"Loop close invoked with '{tag}'")
        # Only close loop after the sanity checks
        super().close(tag, arguments)

    def evaluate(self, context):
        """ Repeats the embedded block as many times as required.

        Args:
            context: The context object at the point of evaluation

        Yields: A line of text at a time
        """
        # Locate the 'in' keyword
        parts = shlex.split(self.loop)
        if "in" not in parts:
            raise PrologueError(f"Incorrectly formed loop condition '{self.loop}'")
        pre_loop  = " ".join(parts[:parts.index("in")])
        post_loop = " ".join(parts[parts.index("in")+1:])
        # TODO: Need to support complex unpacking of loop conditions
        for entry in asteval.Interpreter()(context.flatten(post_loop, skip_undef=True)):
            # Expose the current value of the loop variable
            context.set_define(pre_loop, entry, warning=False)
            # Perform substitutions for the loop variable (and any others)
            for line in super().evaluate(context):
                yield context.substitute(line)
