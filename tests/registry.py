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
from prologue.registry import Registry, RegistryFile

def test_registry_add_bad_file(tmp_path):
    """ Add a bad file path into the registry """
    reg = Registry()
    # Try a file that doesn't exist
    with pytest.raises(PrologueError) as excinfo:
        bad_path = tmp_path / "bad_file.txt"
        reg.add_file(bad_path)
    assert f"File does not exist at path {bad_path}" in str(excinfo.value)
    # Try adding a folder
    with pytest.raises(PrologueError) as excinfo:
        bad_path = tmp_path / "bad_folder"
        bad_path.mkdir()
        reg.add_file(bad_path)
    assert f"Path provided is not a file {bad_path}" in str(excinfo.value)

def test_registry_add_bad_folder(tmp_path):
    """ Add a bad folder into the registry """
    reg = Registry()
    # Try a folder that doesn't exist
    with pytest.raises(PrologueError) as excinfo:
        bad_path = tmp_path / "bad_folder"
        reg.add_folder(bad_path)
    assert f"Folder does not exist at path {bad_path}" in str(excinfo.value)
    # Try adding a file
    with pytest.raises(PrologueError) as excinfo:
        bad_path = tmp_path / "bad_file.txt"
        with open(bad_path, "w") as fh: fh.write("dummy content")
        reg.add_folder(bad_path)
    assert f"Path provided is not a folder {bad_path}" in str(excinfo.value)

def test_registry_add_file(tmp_path):
    """ Add a file to the registry and check it can be resolved """
    reg  = Registry()
    path = tmp_path / "file_a.txt"
    with open(path, "w") as fh: fh.write("dummy content")
    reg.add_file(path)
    r_file = reg.resolve("file_a.txt")
    assert isinstance(r_file, RegistryFile)
    assert r_file.path == path

def test_registry_add_folder(tmp_path):
    """ Add a folder to the registry and check files can be resolved """
    reg    = Registry()
    folder = tmp_path / "folder"
    path   = folder / "test_a.txt"
    folder.mkdir()
    with open(path, "w") as fh: fh.write("dummy content")
    reg.add_folder(folder)
    r_file = reg.resolve("folder/test_a.txt")
    assert isinstance(r_file, RegistryFile)
    assert r_file.path == path

def test_registry_flat(tmp_path):
    """ Test a 'flat' registry sticks all files in the root """
    reg      = Registry(flat=True)
    folder_a = tmp_path / "folder_a"
    folder_b = folder_a / "folder_b"
    file_a   = folder_a / "file_a.txt"
    file_b   = folder_b / "file_b.txt"
    folder_b.mkdir(parents=True)
    with open(file_a, "w") as fh: fh.write("dummy content A")
    with open(file_b, "w") as fh: fh.write("dummy content B")
    reg.add_folder(folder_a)
    r_file_a = reg.resolve("file_a.txt")
    r_file_b = reg.resolve("file_b.txt")
    assert isinstance(r_file_a, RegistryFile)
    assert isinstance(r_file_b, RegistryFile)
    assert r_file_a.path == file_a
    assert r_file_b.path == file_b

def test_registry_recurse(tmp_path):
    """ Test adding a folder recursively """
    reg = Registry()
    # Create nested folders
    folder_a = tmp_path / "folder_a"
    folder_b = folder_a / "folder_b"
    folder_c = folder_b / "folder_c"
    folder_c.mkdir(parents=True)
    # Create a file at each level
    file_a = folder_a / "file_a.txt"
    file_b = folder_b / "file_b.txt"
    file_c = folder_c / "file_c.txt"
    with open(file_a, "w") as fh: fh.write("dummy file a")
    with open(file_b, "w") as fh: fh.write("dummy file b")
    with open(file_c, "w") as fh: fh.write("dummy file c")
    # Add root folder recursively
    reg.add_folder(folder_a, recursive=True)
    r_file_a = reg.resolve("folder_a/file_a.txt")
    r_file_b = reg.resolve("folder_b/file_b.txt")
    r_file_c = reg.resolve("folder_c/file_c.txt")
    assert isinstance(r_file_a, RegistryFile)
    assert isinstance(r_file_b, RegistryFile)
    assert isinstance(r_file_c, RegistryFile)
    assert r_file_a.path == file_a
    assert r_file_b.path == file_b
    assert r_file_c.path == file_c

def test_registry_selective(tmp_path):
    """ Recurse selectively through folder """
    reg = Registry()
    # Create nested folders
    folder_a = tmp_path / "folder_a"
    folder_b = folder_a / "folder_b"
    folder_c = folder_b / "folder_c"
    folder_c.mkdir(parents=True)
    # Create a file at each level
    file_a = folder_a / "file_a.txt"
    file_b = folder_b / "file_b.yml"
    file_c = folder_c / "file_c.txt"
    with open(file_a, "w") as fh: fh.write("dummy file a")
    with open(file_b, "w") as fh: fh.write("dummy file b")
    with open(file_c, "w") as fh: fh.write("dummy file c")
    # Perform a selective add and check
    reg.add_folder(folder_a, search_for=".txt", recursive=True)
    r_file_a = reg.resolve("file_a.txt")
    r_file_c = reg.resolve("file_c.txt")
    assert isinstance(r_file_a, RegistryFile)
    assert isinstance(r_file_c, RegistryFile)
    assert r_file_a.path == file_a
    assert r_file_c.path == file_c
    # Check that file B was not imported
    with pytest.raises(PrologueError) as excinfo:
        reg.resolve("file_b.yml")
    assert f"No entry is known for path file_b.yml" in str(excinfo.value)

def test_registry_bad_insert():
    """ Attempt to insert a bad object type into the Registry """
    reg = Registry()
    for item in ["a string", 123, True, { "hi": "bye" }, [1,2,3]]:
        with pytest.raises(PrologueError) as excinfo:
            reg.insert_entry(item)
        assert f"Entry is not a recognised type {type(item).__name__}" in str(excinfo.value)

def test_registry_clash(tmp_path):
    """ Try to register the same file or folder twice """
    reg = Registry()
    # Insert baseline file and folder
    file_a   = tmp_path / "file_a.txt"
    folder_a = tmp_path / "folder_a"
    with open(file_a, "w") as fh: fh.write("dummy content")
    folder_a.mkdir()
    reg.add_file(file_a)
    reg.add_folder(folder_a)
    # Attempt to insert file a second time
    with pytest.raises(PrologueError) as excinfo:
        reg.add_file(file_a)
    assert f"Entry already exists in registry with name {file_a.parts[-1]}" in str(excinfo.value)
    # Attempt to insert folder a second time
    with pytest.raises(PrologueError) as excinfo:
        reg.add_folder(folder_a)
    assert f"Entry already exists in registry with name {folder_a.parts[-1]}" in str(excinfo.value)

def test_registry_resolve_unknown():
    """ Try to access unregistered file from the registry """
    reg = Registry()
    with pytest.raises(PrologueError) as excinfo:
        reg.resolve("bad_file.txt")
    assert "No entry is known for path bad_file.txt" in str(excinfo.value)

def test_registry_resolve_bad_file(tmp_path):
    """ Try to access a file matching a folder's name """
    reg      = Registry()
    the_path = tmp_path / "some_name"
    the_path.mkdir()
    reg.add_folder(the_path)
    with pytest.raises(PrologueError) as excinfo:
        reg.resolve("some_name")
    assert "Failed to resolve some_name to a file" in str(excinfo.value)

def test_registry_resolve_bad_folder(tmp_path):
    """ Try to access a folder matching a file's name """
    reg      = Registry()
    the_path = tmp_path / "some_name"
    with open(the_path, "w") as fh: fh.write("dummy content")
    reg.add_file(the_path)
    with pytest.raises(PrologueError) as excinfo:
        reg.resolve("some_name/some_file.txt")
    assert "Only a file is registered for path some_name" in str(excinfo.value)
