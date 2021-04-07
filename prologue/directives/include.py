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

@directive("include")
class Include(LineDirective):
    """ Includes the body of another file into the output stream """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, yields=True, src_file=src_file, src_line=src_line,
            callback=callback,
        )
        self.filename = None

    def invoke(self, tag, arguments):
        """ Include a different file into the stream.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity check
        if tag != "include":
            raise PrologueError(f"Include invoked with '{tag}'")
        if self.count_args(arguments) != 1:
            raise PrologueError(f"Invalid form used for #include {arguments}")
        # Store the filename
        self.filename = self.get_arg(arguments, 0)

    def evaluate(self, context):
        """ Include a file.

        Args:
            context: The content object at the point of evaluation.

        Yields: Stream of lines from the included file
        """
        yield from context.pro.evaluate_inner(
            self.filename, context=context, callback=self.callback,
        )

@directive("import")
class Import(LineDirective):
    """ Includes a file, but only once per preprocessing session """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, yields=True, src_file=src_file, src_line=src_line,
            callback=callback,
        )
        self.filename = None

    def invoke(self, tag, arguments):
        """ Include a different file into the stream.

        Args:
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        # Sanity check
        if tag != "import":
            raise PrologueError(f"Import invoked with '{tag}'")
        if self.count_args(arguments) != 1:
            raise PrologueError(f"Invalid form used for #import {arguments}")
        # Store the filename
        self.filename = self.get_arg(arguments, 0)

    def evaluate(self, context):
        """ Import a file (include only once).

        Args:
            context: The content object at the point of evaluation.

        Yields: Stream of lines from the imported file
        """
        r_file = context.pro.registry.resolve(self.filename)
        if r_file not in context.trace:
            yield from context.pro.evaluate_inner(
                self.filename, context=context, callback=self.callback,
            )
