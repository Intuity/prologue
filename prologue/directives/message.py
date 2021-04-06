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

# NOTE: 'return' then 'yield' is used to avoid yielding 'None'

from .base import LineDirective
from .common import directive
from ..common import PrologueError

INFO    = ["info"]
WARNING = ["warn", "warning", "todo", "fixme"]
ERROR   = ["error", "danger", "fatal"]

@directive(*INFO, *WARNING, *ERROR)
class Message(LineDirective):
    """ Prints message at different verbosity levels """

    def __init__(self, parent, src_file=None, src_line=0, callback=None):
        super().__init__(
            parent, src_file=src_file, src_line=src_line, callback=callback,
        )
        self.msg_class = None
        self.msg_text  = None

    def invoke(self, tag, arguments):
        """ Trigger a message to be printed.

        Args:
            context  : The current context object
            tag      : Tag used to trigger this directive
            arguments: Argument string provided to the directive
        """
        global INFO, WARNING, ERROR
        self.msg_text = arguments
        if   tag in INFO   : self.msg_class = "INFO"
        elif tag in WARNING: self.msg_class = "WARNING"
        elif tag in ERROR  : self.msg_class = "ERROR"
        else               : raise PrologueError(f"Unrecognised message type {tag}")

    def evaluate(self, context):
        """ Print the message.

        Args:
            context: The context object at the point of evaluation.
        """
        {
            "INFO"   : context.pro.info_message,
            "WARNING": context.pro.warning_message,
            "ERROR"  : context.pro.error_message,
        }[self.msg_class](self.msg_text, source=self.source)
