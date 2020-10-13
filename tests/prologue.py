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

from prologue import Prologue
from prologue.common import PrologueError

def test_prologue_bad_delimiter():
    """ Try to setup Prologue with a bad delimiter """
    # Use an empty delimiter
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter="")
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use just whitespace
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter="     ")
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use mix of whitespace and characters
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter=" / /")
    assert "Delimiter should not contain whitespace" in str(excinfo.value)
    # Check a sane value works
    assert Prologue(delimiter="//").delimiter == "//"

def test_prologue_bad_new_delimiter():
    """ Try to change the Prologue delimiter to a bad value """
    pro = Prologue(delimiter="#")
    # Read back the delimiter
    assert pro.delimiter == "#"
    # Use an empty delimiter
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = ""
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use just whitespace
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = "     "
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use mix of whitespace and characters
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = " / /"
    assert "Delimiter should not contain whitespace" in str(excinfo.value)
    # Check a sane value works
    pro.delimiter = "//"
    assert pro.delimiter == "//"

def test_prologue_bad_shared():
    """ Try to setup Prologue with a bad shared value """
    # Check a bad value doesn't work
    with pytest.raises(PrologueError) as excinfo:
        Prologue(shared_delimiter="banana")
    assert "Shared delimiter should be True or False"
    # Check both sane values work
    for val in (True, False):
        assert Prologue(shared_delimiter=val).shared_delimiter == val

def test_prologue_bad_new_shared():
    """ Try to change Prologue's shared delimiter value """
    pro = Prologue()
    # Check a bad value doesn't work
    with pytest.raises(PrologueError) as excinfo:
        pro.shared_delimiter = "banana"
    assert "Shared delimiter should be True or False"
    # Check both sane values work
    for val in (True, False):
        pro.shared_delimiter = val
        assert pro.shared_delimiter == val

def test_prologue_add_file(mocker):
    """ Test that add file calls to the registry """
    pro = Prologue()
    mocker.patch.object(pro, "registry", autospec=True)
    pro.add_file("test_file_1234")
    pro.registry.add_file.assert_called_once_with("test_file_1234")

def test_prologue_add_folder(mocker):
    """ Test that add folder calls to the registry """
    pro = Prologue()
    mocker.patch.object(pro, "registry", autospec=True)
    pro.add_folder("test_folder_1234", ".txt", True)
    pro.registry.add_folder.assert_called_once_with(
        "test_folder_1234", search_for=".txt", recursive=True
    )
