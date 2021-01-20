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

from random import choice, randint
from string import ascii_letters

def random_str(min_len, max_len, avoid=None):
    """ Generate a random string of the specified length.

    Args:
        min_len: Minimum length of string
        max_len: Maximum length of string
        avoid  : Optional list of strings to avoid

    Returns: Random ASCII string
    """
    while True:
        r_str = "".join([
            choice(ascii_letters) for _x in range(randint(min_len, max_len))
        ])
        if not isinstance(avoid, list) or r_str not in avoid:
            return r_str
