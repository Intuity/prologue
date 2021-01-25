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

import pytest

from prologue.common import Line

from .common import random_str

def test_line():
    """ Test that a line holds a string, file, and line number """
    lines = []
    for _x in range(100):
        l_str  = random_str(10, 20)
        l_file = random_str(10, 20)
        l_num  = randint(1, 10000)
        lines.append((Line(l_str, l_file, l_num), l_str, l_file, l_num))
    while len(lines) > 0:
        entry                      = choice(lines)
        line, l_str, l_file, l_num = entry
        assert line            == l_str
        assert str(line)       == l_str
        assert line.file       == l_file
        assert line.number     == l_num
        assert line.__repr__() == f"{l_file}@{l_num}: {str(line)}"
        lines.remove(entry)

def test_line_encase():
    """ Test that an encased string carries the same file and number """
    for _x in range(100):
        l_file = random_str(10, 20)
        l_num  = randint(1, 10000)
        line   = Line(random_str(10, 20), l_file, l_num)
        for _y in range(20):
            sub_str  = random_str(10, 20)
            sub_line = line.encase(sub_str)
            assert isinstance(sub_line, Line)
            assert sub_line        == sub_str
            assert str(sub_line)   == sub_str
            assert sub_line.file   == l_file
            assert sub_line.number == l_num

def test_line_substring():
    """ Test retrieval of characters and ranges from string """
    for _x in range(100):
        l_str = random_str(50, 100)
        line  = Line(l_str, random_str(10, 20), randint(1, 10000))
        # Try a single charater
        c_idx    = randint(0, len(l_str)-1)
        sub_line = line[c_idx]
        assert sub_line == l_str[c_idx]
        assert isinstance(sub_line, Line)
        assert sub_line.file   == line.file
        assert sub_line.number == line.number
        # Try a range
        s_idx    = randint(0, (len(l_str) // 2) - 1)
        e_idx    = randint(len(l_str) // 2, len(l_str) - 1)
        sub_line = line[s_idx:e_idx]
        assert sub_line        == l_str[s_idx:e_idx]
        assert sub_line.file   == line.file
        assert sub_line.number == line.number

def test_line_split():
    """ Test splitting the line on a delimiter """
    for _x in range(100):
        delim = choice(("=", "|", ",", "$", ".", "/"))
        l_str = delim.join([random_str(5, 10) for x in range(30)])
        line  = Line(l_str, random_str(10, 20), randint(1, 10000))
        # Split the string
        l_parts   = line.split(delim)
        exp_parts = l_str.split(delim)
        assert len(l_parts) == len(exp_parts)
        for l_part, x_part in zip(l_parts, exp_parts):
            assert isinstance(l_part, Line)
            assert l_part        == x_part
            assert l_part.file   == line.file
            assert l_part.number == line.number

def test_line_strip():
    """ Test stripping the line """
    for _x in range(100):
        l_str = " ".join([random_str(5, 10) for x in range(30)])
        l_str = (" " * randint(0, 10)) + l_str + (" " * randint(0, 10))
        line  = Line(l_str, random_str(10, 20), randint(1, 10000))
        # Strip the string
        l_stripped = line.strip()
        assert l_stripped == l_str.strip()
        assert isinstance(l_stripped, Line)
        assert l_stripped.file   == line.file
        assert l_stripped.number == line.number

def test_line_concat():
    """ Test concatenating different lines """
    for _x in range(100):
        strings = [random_str(30, 50) for _x in range(10)]
        l_file  = random_str(10, 20)
        l_num   = randint(1, 10000)
        lines   = [Line(x, l_file, l_num) for x in strings]
        # Concatenate the lines
        l_full = lines[0]
        for line in lines[1:]: l_full = l_full + line
        # Test the result
        assert l_full == "".join(strings)
        assert isinstance(l_full, Line)
        assert l_full.file   == l_file
        assert l_full.number == l_num

