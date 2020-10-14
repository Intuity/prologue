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

from .common import line_directive

@line_directive("info")
def info_directive(tag, arguments):
    print(f"INFO: {arguments}")
    return
    yield

@line_directive("warn", "warning", "todo", "fixme")
def warn_directive(tag, arguments):
    print(f"WARNING: {arguments}")
    return
    yield

@line_directive("error", "danger")
def error_directive(tag, arguments):
    print(f"ERROR: {arguments}")
    return
    yield
