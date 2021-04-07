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

from enum import IntEnum
from pathlib import Path

from .common import PrologueError, Line

class RegistryFile(object):
    """ Holds a file in the registry """

    def __init__(self, path):
        """ Initialise the registry file

        Args:
            path: Path to the file
        """
        # Ensure that the path is a Path instance
        self.path = Path(path) if not isinstance(path, Path) else path
        # Check the path exists
        if not self.path.exists():
            raise PrologueError(
                f"File does not exist at path {self.path}"
            )
        # Check that the path is a file
        if not self.path.is_file():
            raise PrologueError(
                f"Path provided is not a file {self.path}"
            )

    @property
    def filename(self): return self.path.parts[-1]

    @property
    def contents(self):
        """ Provide an iterable that reads a line at a time from the file """
        with open(self.path, "r") as fh:
            for idx, line in enumerate(fh.readlines()):
                yield Line(line.rstrip(), self, idx + 1)

    def snippet(self, line, before=2, after=2):
        """ Generate a snippet of the original file.

        Args:
            line  : Line number to extract
            before: Number of lines before the line to include
            after : Number of lines after the line to include

        Returns: List of lines forming snippet
        """
        snippet = []
        for s_line in self.contents:
            # If this is before the snip point, ignore it
            if s_line.number < (line - before): continue
            # If this is after the snip point, break out
            if s_line.number > (line + after): break
            # Otherwise, build up the snippet
            snippet.append("%4i %s %s" % (
                s_line.number, (">>" if (s_line.number == line) else "  "),
                str(s_line)
            ))
        return snippet

class RegistryFolder(object):
    """ Holds a folder in the registry """

    def __init__(self, path):
        """ Initialise the registry folder

        Args:
            path: Path to the folder
        """
        # Ensure that the path is a Path instance
        self.path = Path(path) if not isinstance(path, Path) else path
        # Check the path exists
        if not self.path.exists():
            raise PrologueError(
                f"Folder does not exist at path {self.path}"
            )
        # Check that the path is a directory
        if not self.path.is_dir():
            raise PrologueError(
                f"Path provided is not a folder {self.path}"
            )

    @property
    def folder(self): return self.path.parts[-1]

    def resolve(self, path):
        """ Resolve a relative path within this folder to get a file.

        Args:
            path: The path to resolve
        """
        # Ensure this is a Path object
        path = Path(path) if not isinstance(path, Path) else path
        # Check if this is absolute
        if path.is_absolute():
            raise PrologueError(f"Attempted to resolve absolute path {path}")
        # Check how many segments are left
        if len(path.parts) > 1:
            return RegistryFolder(self.path / path.parts[0]).resolve(
                Path(*path.parts[1:])
            )
        else:
            return RegistryFile(self.path / path.parts[0])

class Registry(object):
    """ Keeps track of all files available to IMPORT and INCLUDE """

    def __init__(self, pro, flat=False):
        """ Initialise the registry

        Args:
            pro : Pointer to the Prologue instance
            flat: Flatten all hierarchy of folders added to the registry.
        """
        self.__pro     = pro
        self.__flat    = flat
        self.__entries = {}

    def insert_entry(self, entry, ignore_duplicate=False):
        """ Insert an entry into the registry.

        Args:
            entry           : Either a RegistryFile or RegistryFolder instance
            ignore_duplicate: Don't raise an error if the file or folder already
                              exists in the registry (default: False)
        """
        # Check the entry type
        if type(entry) not in [RegistryFile, RegistryFolder]:
            raise PrologueError(
                f"Entry is not a recognised type {type(entry).__name__}"
            )
        # Check that the entry doesn't collide
        entry_name = (
            entry.filename if isinstance(entry, RegistryFile) else entry.folder
        )
        if entry_name in self.__entries:
            if ignore_duplicate: return
            raise PrologueError(
                f"Entry already exists in registry with name {entry_name}"
            )
        # Insert the entry
        self.__pro.debug_message(
            f"Adding entry '{entry_name}' to registry: {entry.path}"
        )
        self.__entries[entry_name] = entry

    def list_entries(self):
        """ List all files and folders present in the registry.

        Returns: List of RegistryFile and RegistryFolder entries
        """
        return list(self.__entries.values())

    def has_entry(self, name):
        """ Check if the registry contains an entry for a given name.

        Returns: True if it exists, False otherwise
        """
        return name in self.__entries

    def add_file(self, path, ignore_duplicate=False):
        """ Add a specific file to the registry.

        Args:
            path            : Path to the file to add
            ignore_duplicate: Don't raise an error if the file or folder already
                              exists in the registry (default: False)
        """
        self.insert_entry(RegistryFile(path), ignore_duplicate=ignore_duplicate)

    def add_folder(
        self, path, search_for=None, recursive=False, ignore_duplicate=False
    ):
        """
        Add a new folder to the registry. If 'search_for' is provided, then all
        matching files within the folder will be added to the registry root,
        optionally if 'recursive' is provided the whole tree beneath the folder
        will be traversed. If only 'recursive' is provided, all folders within
        the top level folder will be added. If neither argument is provided,
        only the top-level folder will be added.

        Args:
            path            : Path to the root folder to add
            search_for      : Provide a file extension to search for
            recursive       : Whether to search recursively in this folder
            ignore_duplicate: Don't raise an error if the file or folder already
                              exists in the registry (default: False)
        """
        self.__pro.debug_message(
            "Adding folder " + ("" if recursive else "non-") + "recursively to "
            f"registry, searching for {search_for}: {path}"
        )
        # Wrap the folder
        r_folder = RegistryFolder(path)
        # If neither argument provided, register directly
        if not self.__flat and not search_for and not recursive:
            self.insert_entry(r_folder, ignore_duplicate=ignore_duplicate)
        # If only recursive is provided, register all subfolders
        elif not self.__flat and not search_for and recursive:
            for subfolder in r_folder.path.rglob("**/"):
                self.insert_entry(
                    RegistryFolder(subfolder), ignore_duplicate=ignore_duplicate
                )
        # If search_for is provided, lookup files
        elif self.__flat or isinstance(search_for, str):
            if not search_for: search_for = ""
            for subpath in (
                r_folder.path.rglob(f"**/*{search_for}")
                if (self.__flat or recursive) else
                r_folder.path.glob(f"*{search_for}")
            ):
                if subpath.is_dir(): continue
                self.insert_entry(
                    RegistryFile(subpath), ignore_duplicate=ignore_duplicate
                )
        # Unknown scenario
        else:
            raise PrologueError(f"Unexpected error adding folder {path}")

    def resolve(self, path):
        """ Resolve a path within the registry to get a file.

        Args:
            path: The path to resolve
        """
        # Ensure this is a Path instance
        path = Path(str(path).strip())
        # Check if the path is absolute
        if path.is_absolute(): return RegistryFile(path)
        # Otherwise, attempt to resolve
        if path.parts[0] not in self.__entries:
            raise PrologueError(f"No registry entry found for '{path}'")
        # Lookup the entry
        entry = self.__entries[path.parts[0]]
        # Sanity check
        if len(path.parts) > 1:
            if isinstance(entry, RegistryFile):
                raise PrologueError(f"Only a file is registered for path {path.parts[0]}")
            return entry.resolve(Path(*path.parts[1:]))
        elif isinstance(entry, RegistryFolder):
            raise PrologueError(f"Failed to resolve {path} to a file")
        else:
            return entry
