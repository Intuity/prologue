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
from prologue.registry import RegistryFolder

def test_reg_folder_bad_path(tmp_path):
    """ Test that RegistryFolder raises error about missing directory """
    bad_folder = tmp_path / "my_folder"
    with pytest.raises(PrologueError) as excinfo:
        RegistryFolder(bad_folder)
    assert f"Folder does not exist at path {bad_folder}" in str(excinfo.value)

def test_reg_folder_bad_type(tmp_path):
    """ Test that RegistryFolder raises error about bad folder type """
    bad_path = tmp_path / "my_file.txt"
    with open(bad_path, "w") as fh: fh.write("dummy content")
    with pytest.raises(PrologueError) as excinfo:
        RegistryFolder(bad_path)
    assert f"Path provided is not a folder {bad_path}" in str(excinfo.value)

def test_reg_folder(tmp_path):
    """ Test that RegistryFolder can locate a real folder """
    real_path = tmp_path / "my_folder"
    real_path.mkdir()
    r_folder = RegistryFolder(real_path)
    assert r_folder.folder == "my_folder"

def test_reg_folder_string(tmp_path):
    """ Test that RegistryFolder accepts a path as a string """
    real_path = tmp_path / "my_folder"
    real_path.mkdir()
    r_folder = RegistryFolder(str(real_path.as_posix()))
    assert r_folder.folder == "my_folder"

def test_reg_folder_resolve(tmp_path):
    """ Test that RegistryFolder can resolve relative paths """
    folder_a = tmp_path / "folder_a"
    folder_b = folder_a / "folder_b"
    file_a   = folder_a / "file_a.txt"
    file_b   = folder_b / "file_b.txt"
    folder_b.mkdir(parents=True)
    with open(file_a, "w") as fh: fh.write("dummy content A")
    with open(file_b, "w") as fh: fh.write("dummy content B")
    r_folder_a = RegistryFolder(folder_a)
    r_file_a  = r_folder_a.resolve("file_a.txt")
    r_file_b  = r_folder_a.resolve("folder_b/file_b.txt")
    assert r_file_a.path     == file_a
    assert r_file_a.filename == "file_a.txt"
    assert r_file_b.path     == file_b
    assert r_file_b.filename == "file_b.txt"

def test_reg_folder_resolve_absolute(tmp_path):
    """ Try to resolve an absolute path within a folder """
    real_path = tmp_path / "my_folder"
    real_path.mkdir()
    r_folder = RegistryFolder(real_path)
    with pytest.raises(PrologueError) as excinfo:
        r_folder.resolve(real_path.absolute().as_posix())
    assert f"Attempted to resolve absolute path {real_path.absolute().as_posix()}" in str(excinfo.value)