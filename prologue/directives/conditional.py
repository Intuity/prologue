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

@directive(
    opening   =["if", "ifdef", "ifndef"],
    transition=["elif", "else"],
    closing   =["endif"]
)
class Conditional(BlockDirective):
    """ Conditional directive supporting IF/ELIF/ELSE/ENDIF sections """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, src_file=src_file, src_line=src_line, callback=callback
        )
        self.if_section    = None
        self.elif_sections = []
        self.else_section  = None

    def open(self, tag, arguments):
        """ Open the conditional block with an 'if' clause.

        Args:
            tag      : The tag that opens the directive
            arguments: Argument string following the directive
        """
        # Sanity checks
        if tag not in ("if", "ifdef", "ifndef"):
            raise PrologueError(f"Conditional opening invoked with '{tag}'")
        # Now open the tag
        super().open(tag, arguments)
        # Record the section
        self.if_section = tag, arguments, Block(self)

    def transition(self, tag, arguments):
        """ Transition between different sections with ELIF/ELSE.

        Args:
            tag      : The tag that opens the section
            arguments: Argument string following the directive
        """
        # Sanity checks
        if tag not in ["elif", "else"]:
            raise PrologueError(f"Conditional transition invoked with '{tag}'")
        elif self.else_section:
            raise PrologueError(f"Transition '{tag}' detected after 'else' clause")
        # Now perform transition
        super().transition(tag, arguments)
        # Register the tag
        if tag == "elif":
            self.elif_sections.append((tag, arguments, Block(self)))
        else:
            self.else_section = tag, arguments, Block(self)

    def close(self, tag, arguments):
        """ Close the directive block with ENDIF.

        Args:
            tag      : The tag that opens the section
            arguments: Argument string following the directive
        """
        # Sanity checks
        if tag != "endif":
            raise PrologueError(f"Conditional close invoked with '{tag}'")
        # Now close tag
        super().close(tag, arguments)

    def append(self, entry):
        """ Append a new line or nested block to the active section.

        Args:
            entry: The line or block to append.
        """
        # Sanity checks
        if not self.opened:
            raise PrologueError("Trying to append a line to an unopened conditional")
        elif self.closed:
            raise PrologueError("Trying to append a line to a closed conditional")
        # Append to the latest open block
        if   self.else_section          : self.else_section[2].append(entry)
        elif len(self.elif_sections) > 0: self.elif_sections[-1][2].append(entry)
        else                            : self.if_section[2].append(entry)

    def evaluate(self, context):
        """ Selects the correct block to evaluate based upon conditions.

        Args:
            context: The context object at the point of evaluation

        Yields: A line of text at a time
        """
        # Put sections in the correct order to evaluate
        sections = [self.if_section, *self.elif_sections]
        if self.else_section: sections.append(self.else_section)
        # Check which section is active
        for tag, cond, block in sections:
            # Replace alternative syntaxes for Python operators
            cond = cond.replace("&&", " and ").replace("||", " or ")
            # Evaluate the conditional
            if (
                (tag == "ifdef"  and     context.has_define(cond)) or
                (tag == "ifndef" and not context.has_define(cond)) or
                (tag not in ("ifdef", "ifndef") and context.evaluate(cond)) or
                (tag == "else")
            ):
                yield from block.evaluate(context)
                context.join()
                break
