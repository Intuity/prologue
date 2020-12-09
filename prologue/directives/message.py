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

INFO  = ["info"]
WARN  = ["warn", "warning", "todo", "fixme"]
ERROR = ["error", "danger", "fatal"]

@directive(*INFO, *WARN, *ERROR)
class Message(LineDirective):

    def invoke(self, context, tag, arguments):
        global INFO, WARN, ERROR
        if tag in INFO:
            print(f"INFO{self.uuid}: {arguments}")
        elif tag in WARN:
            print(f"WARNING{self.uuid}: {arguments}")
        elif tag in ERROR:
            print(f"ERROR{self.uuid}: {arguments}")
        else:
            raise PrologueError(f"Unrecognised message type tag {tag}")
        yield
        return
