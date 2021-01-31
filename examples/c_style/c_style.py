# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

from pathlib import Path
import sys

from prologue import Prologue

# Check for right number of arguments, then extract them
if len(sys.argv) != 3:
    print("SYNTAX: python3 c_style.py <INPUTDIR> <TOPFILE>")
    sys.exit(1)

in_dir = Path(sys.argv[1])
top    = Path(sys.argv[2])

# Setup preprocessor instance
pro = Prologue(delimiter="#", shared_delimiter=False)

# Find all files within the input directory and add them to the registry
for f_path in in_dir.glob("*.*"):
    pro.add_file(f_path)

# Kick off evaluate using the top-level file
for line in pro.evaluate(top.parts[-1]):
    print(line)
