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

import re

from .common import PrologueError
from .directives import register_prime_directives
from .directives.common import DirectiveType, Directive
from .registry import Registry

class Prologue(object):
    """ Top-level of the preprocessor """

    def __init__(self, delimiter="#", shared_delimiter=False):
        """ Initialise the preprocessor.

        Args:
            delimiter       : Specify the character to use as the delimiter
                              (default: '#')
            shared_delimiter: Delimiter is also used to signify a comment
                              (default: False)
        """
        # Store attributes
        self.delimiter        = delimiter
        self.shared_delimiter = shared_delimiter
        # Create a registry instance
        self.registry = Registry()
        # Create a store for directives
        self.directives = {}
        register_prime_directives(self)

    # ==========================================================================
    # Property Setters/Getters
    # ==========================================================================

    @property
    def delimiter(self): return self.__delimiter

    @delimiter.setter
    def delimiter(self, val):
        # Check delimiter
        if len(val.strip()) == 0:
            raise PrologueError("Delimiter should be at least one character")
        elif len(val.replace(" ", "")) != len(val):
            raise PrologueError("Delimiter should not contain whitespace")
        # Set delimiter
        self.__delimiter = val

    @property
    def shared_delimiter(self): return self.__shared_delimiter

    @shared_delimiter.setter
    def shared_delimiter(self, val):
        # Check value is True or False
        if not isinstance(val, bool):
            raise PrologueError("Shared delimiter should be True or False")
        # Set value
        self.__shared_delimiter = val

    # ==========================================================================
    # Registry Passthroughs
    # ==========================================================================

    def add_file(self, path):
        """ Add a file to the registry.

        Args:
            path: Path to add
        """
        self.registry.add_file(path)

    def add_folder(self, path, search_for=None, recursive=False):
        """ Add a folder to the registry, see Registry.add_folder for more info.

        Args:
            path      : Path to the root folder to add
            search_for: Provide a file extension to search for
            recursive : Whether to search recursively in this folder
        """
        self.registry.add_folder(path, search_for=search_for, recursive=recursive)

    # ==========================================================================
    # Directives
    # ==========================================================================

    def register_directive(self, dirx):
        """ Register a directive for handling lines or blocks.

        Args:
            dirx: Decorated function that will act as the directive
        """
        # Check that the directive is correctly decorated
        if not isinstance(dirx, Directive):
            raise PrologueError("Directive type is not known, is it decorated?")
        # Check all tags
        for tag in dirx.tags:
            # Check if the tag collides with an existing directive
            if tag in self.directives:
                raise PrologueError(f"Directive already registered for tag '{tag}'")
            # Check if the tag collides with a directive closing tag
            if (
                tag.startswith("end") and (tag[3:] in self.directives) and
                (self.directives[tag[3:]].type == DirectiveType.BLOCK)
            ):
                raise PrologueError(
                    f"Directive tag '{tag}' clashes with terminator of block "
                    f"directive '{tag[3:]}'"
                )
        # Check directive is callable
        if not callable(dirx):
            raise PrologueError(
                f"Directive provided is not callable: {type(dirx).__name__}"
            )
        # Register the directive
        for tag in dirx.tags: self.directives[tag] = dirx

    def get_directive(self, tag):
        """
        Return a directive for a particular tag. If the delimiter is not shared
        and the tag isn't known, an error will be raised. If the delimiter is
        shared, then None will be returned.

        Args:
            tag: The tag of the directive

        Returns: Directive function if known, otherwise None
        """
        # If this is an 'end' directive, convert tag
        if tag.startswith("end") and tag[3:] in self.directives: tag = tag[3:]
        # Check if a directive exists for this tag
        if tag not in self.directives:
            if self.shared_delimiter:
                return None
            else:
                raise PrologueError(f"No directive known for tag '{tag}'")
        # Return the directive
        return self.directives[tag]

    # ==========================================================================
    # Evaluation
    # ==========================================================================

    def evaluate(self, top_level):
        """ Iterable evaluation function which returns fully preprocessed stream

        Args:
            top_level: The top level filename to start from
        """
        # Find the top-level file
        r_file = self.registry.resolve(top_level)
        if not r_file:
            raise PrologueError(f"Failed to find top-level file {top_level}")
        # Create regular expressions for recognising directives
        re_anchored = re.compile(
            f"^[\s]*{self.delimiter}[\s]*([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        re_floating = re.compile(
            f"^(.*?){self.delimiter}[\s]*([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        # Create stack to keep track of parse context
        stack = []
        # Start parsing
        for idx, line in enumerate(r_file.contents):
            # Test if the line matches an anchored directive
            anchored = re_anchored.match(line)
            if anchored:
                tag, arguments = anchored.groups()
                yield from self.get_directive(tag)(tag, arguments.strip())
                continue
            # Test if the line matches a floating directive
            floating = re_floating.match(line)
            if floating:
                prior, tag, arguments = floating.groups()
                directive             = self.get_directive(tag)
                if directive.type == DirectiveType.BLOCK:
                    raise PrologueError(
                        f"The directive '{tag}' can only be used with an "
                        f"delimiter as it is a block directive"
                    )
                # Yield the text before the directive
                yield prior.rstrip()
                # Yield the contents returned from the directive
                yield from directive(tag, arguments.strip())
                continue
            # Otherwise, this is just a line!
            yield line
