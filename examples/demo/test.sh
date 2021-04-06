#!/bin/bash

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

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Setup PYTHONPATH to get access to Prologue
export PYTHONPATH=${this_dir}/../..:$PYTHONPATH

# Run the preprocessor
python3 demo.py ${this_dir}/input ${this_dir}/input/first.txt ${this_dir}/test.txt

# Compare with the expected output
diff -q ${this_dir}/test.txt ${this_dir}/expected/first.txt >& /dev/null
if [[ "$?" == "1" ]]; then
    echo "[ERROR] Demo expected output did not match Prologue output"
    exit 1
else
    echo "[OKAY] Demo output matched expectation"
fi

# Clean-up
rm test.txt
