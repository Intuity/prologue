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
from .context import Context
from .directives import register_prime_directives
from .directives.base import Directive
from .directives.common import DirectiveWrap
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
        # Create empty message handling callbacks
        self.callback_debug   = None
        self.callback_info    = None
        self.callback_warning = None
        self.callback_error   = None
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
    # Message Handlers
    # NOTE: Errors are raised as exceptions using PrologueError
    # ==========================================================================

    def debug_message(self, message, **kwargs):
        """ Handle debug level messages.

        Args:
            message: The message to print
            kwargs : Attributes related to the message
        """
        # If a callback is configured, delegate message to it
        if self.callback_debug:
            self.callback_debug(message, **kwargs)
        # Otherwise print it out
        else:
            print(f"[PROLOGUE:DEBUG] {message}")

    def info_message(self, message, **kwargs):
        """ Handle info level messages.

        Args:
            message: The message to print
            kwargs : Attributes related to the message
        """
        # If a callback is configured, delegate message to it
        if self.callback_info:
            self.callback_info(message, **kwargs)
        # Otherwise print it out
        else:
            print(f"[PROLOGUE:INFO] {message}")

    def warning_message(self, message, **kwargs):
        """ Handle warning level messages.

        Args:
            message: The message to print
            kwargs : Attributes related to the message
        """
        # If a callback is configured, delegate message to it
        if self.callback_warning:
            self.callback_warning(message, **kwargs)
        # Otherwise print it out
        else:
            print(f"[PROLOGUE:WARN] {message}")

    def error_message(self, message, **kwargs):
        """ Handle error level messages.

        Args:
            message: The message to print
            kwargs : Attributes related to the message
        """
        # If a callback is configured, delegate message to it
        if self.callback_error:
            self.callback_error(message, **kwargs)
        # Otherwise print it out
        else:
            raise PrologueError(message)

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
        if not isinstance(dirx, DirectiveWrap):
            raise PrologueError("Directive type is not known, is it decorated?")
        # Check all tags
        for tag in dirx.tags:
            # Check if the tag collides with an existing directive
            if tag in self.directives:
                raise PrologueError(f"Directive already registered for tag '{tag}'")
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

    def evaluate(self, filename):
        """ Iterable evaluation function which returns fully preprocessed stream

        Args:
            filename: The file to evaluate

        Yields: Stream of fully preprocessed lines
        """
        # Create a context object used for tracking variables and parse state
        context = Context(self)
        # Use inner evaluation routine to get each line one at a time
        for line in self.evaluate_inner(filename, context):
            yield context.substitute(line)

    def evaluate_inner(self, filename, context):
        """
        Inner evaluation routine - this performs all construction and evaluation
        except variable substitution, which is performed by 'evaluate'.

        Args:
            filename: The file to evaluate
            context : A context object

        Yields: Stream of preprocessed lines, prior to substitution
        """
        # Find the top-level file
        r_file = self.registry.resolve(filename)
        if not r_file: raise PrologueError(f"Failed to find file {filename}")
        # Sanity check a context object was provided
        if not isinstance(context, Context):
            raise PrologueError(f"An invalid context was provided: {context}")
        # Create regular expressions for recognising directives
        re_anchored = re.compile(
            f"^[\s]*{self.delimiter}[\s]*([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        re_floating = re.compile(
            f"^(.*?){self.delimiter}[\s]*([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        # Stop infinite recursion by checking if this file is already in the stack
        if r_file in context.stack:
            raise PrologueError(
                f"Detected infinite recursion when including file '{filename}' "
                f"- file stack: {', '.join([x.filename for x in context.stack])}"
            )
        # Push the current file into the stack
        context.stack_push(r_file)
        # Start parsing
        active      = None
        accumulated = None
        for idx, line in enumerate(r_file.contents):
            # Handle line continuation
            if line and line[-1] == "\\":
                accumulated = (accumulated + line[:-1]) if accumulated else line[:-1]
                continue
            elif accumulated:
                line        = accumulated + line
                accumulated = None
            # Test if the line matches an anchored directive
            anchored = re_anchored.match(line)
            if anchored:
                tag, arguments = anchored.groups()
                arguments      = arguments.strip()
                tag            = tag.lower()
                d_wrap         = self.get_directive(tag)
                if arguments.endswith(":"): arguments = arguments[:-1]
                if d_wrap.is_line:
                    l_dir = d_wrap.directive(active)
                    l_dir.invoke(tag, arguments.strip())
                    if   active      : active.append(l_dir)
                    elif l_dir.yields: yield from l_dir.evaluate(context)
                    else             : l_dir.evaluate(context)
                elif d_wrap.is_block:
                    # Call the directive
                    if d_wrap.is_opening(tag):
                        block   = d_wrap.directive(active)
                        block.open(tag, arguments)
                        # If a block is already open, append to it
                        if active: active.append(block)
                        # Track currently active block
                        active = block
                    elif d_wrap.is_transition(tag):
                        if d_wrap.directive != type(active):
                            raise PrologueError(f"Transition tag '{tag}' was not expected")
                        active.transition(tag, arguments)
                    elif d_wrap.is_closing(tag):
                        if d_wrap.directive != type(active):
                            raise PrologueError(f"Closing tag '{tag}' was not expected")
                        active.close(tag, arguments)
                        # If there is no parent, this is the root
                        if not active.parent:
                            if active.yields:
                                yield from active.evaluate(context.fork())
                            else:
                                active.evaluate(context.fork())
                        # Pop the stack
                        active = active.parent
                    else:
                        raise PrologueError("Unrecognised directive transition")
                else:
                    raise PrologueError(f"Unknown directive type for tag {tag}")
                continue
            # Test if the line matches a floating directive
            floating = re_floating.match(line)
            if floating:
                prior, tag, arguments = floating.groups()
                arguments             = arguments.strip()
                d_wrap                = self.get_directive(tag)
                if d_wrap.is_block:
                    raise PrologueError(
                        f"The directive '{tag}' can only be used with a "
                        f"delimiter as it is a block directive"
                    )
                if arguments.endswith(":"): arguments = arguments[:-1]
                # Yield the text before the directive
                yield prior.rstrip()
                # Yield the contents returned from the directive
                l_dir = d_wrap.directive(active)
                l_dir.invoke(tag, arguments.strip())
                if   active      : active.append(l_dir)
                elif l_dir.yields: yield from l_dir.evaluate(context)
                else             : l_dir.evaluate(context)
                continue
            # Otherwise, this is just a line!
            if active: active.append(line)
            else     : yield line
        # Check for trailing directives
        if active:
            dir_stack = [x for x in active.stack if isinstance(x, Directive)]
            raise PrologueError(
                f"Some directives remain unclosed at end of {top_level}: "
                + ', '.join((type(x).OPENING[0] for x in dir_stack))
            )
        # Pop the file being parsed from the stack
        if context.stack_pop() != r_file:
            raise PrologueError("File stack has been corrupted")
