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

import pytest

from prologue.common import PrologueError
from prologue.registry import RegistryFile

def test_reg_file_bad_path(tmp_path):
    """ Test that RegistryFile raises error about missing file """
    bad_file = tmp_path / "my_file.txt"
    with pytest.raises(PrologueError) as excinfo:
        RegistryFile(bad_file)
    assert f"File does not exist at path {bad_file}" in str(excinfo.value)

def test_reg_file_bad_type(tmp_path):
    """ Test that RegistryFile raises error about bad file type """
    bad_path = tmp_path / "my_folder"
    bad_path.mkdir()
    with pytest.raises(PrologueError) as excinfo:
        RegistryFile(bad_path)
    assert f"Path provided is not a file {bad_path}" in str(excinfo.value)

def test_reg_file(tmp_path):
    """ Test that RegistryFile can locate a real file """
    real_path = tmp_path / "my_file.txt"
    with open(real_path, "w") as fh: fh.write("dummy content")
    r_file = RegistryFile(real_path)
    assert r_file.filename == "my_file.txt"

def test_reg_file_string(tmp_path):
    """ Test that RegistryFile accepts a path as a string """
    real_path = tmp_path / "my_file.txt"
    with open(real_path, "w") as fh: fh.write("dummy content")
    r_file = RegistryFile(str(real_path.as_posix()))
    assert r_file.filename == "my_file.txt"
