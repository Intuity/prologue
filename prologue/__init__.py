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

from .common import PrologueError, Line
from .context import Context
from .directives import register_prime_directives
from .directives.base import Directive
from .directives.common import DirectiveWrap
from .registry import Registry

class Prologue(object):
    """ Top-level of the preprocessor """

    def __init__(
        self,
        comment         ="#",
        delimiter       ="#",
        shared_delimiter=False,
        implicit_sub    =True,
        explicit_style  =("$(", ")"),
        allow_redefine  =False,
        register_prime  =True,
    ):
        """ Initialise the preprocessor.

        Args:
            comment         : The single line comment sequence (default: '#')
            delimiter       : Specify the sequence to use as the delimiter
                              (default: '#')
            shared_delimiter: Delimiter is also used to signify a comment
                              (default: False)
            implicit_sub    : Allow implicit substitutions (default: True)
            explit_style    : Style used for identifying explicit substitutions,
                              this should be a tuple of the prefix and suffix of
                              the format (default: '$(', ')')
            allow_redefine  : Allow values to be defined multiple times (by
                              default raises a PrologueError, default: False)
            register_prime  : Register the prime directives (default: True)
        """
        # Sanity checks
        if not isinstance(comment, str):
            raise PrologueError(f"Comment sequence must be a string: {comment}")
        if not isinstance(delimiter, str):
            raise PrologueError(f"Delimiter sequence must be a string: {delimiter}")
        if shared_delimiter not in (True, False):
            raise PrologueError(f"Shared delimiter must be True or False: {shared_delimiter}")
        if implicit_sub not in (True, False):
            raise PrologueError(f"Implicit substitution must be True or False: {implicit_sub}")
        if not isinstance(explicit_style, tuple):
            raise PrologueError(f"Explicit style must be a tuple: {explicit_style}")
        if allow_redefine not in (True, False):
            raise PrologueError(f"Allow redefinition must be True or False: {allow_redefine}")
        if register_prime not in (True, False):
            raise PrologueError(f"Register prime must be True or False: {register_prime}")
        # Store attributes
        self.comment          = comment
        self.delimiter        = delimiter
        self.shared_delimiter = shared_delimiter
        self.implicit_sub     = implicit_sub
        self.explicit_style   = explicit_style
        self.allow_redefine   = allow_redefine
        # Create empty message handling callbacks
        self.callback_debug   = None
        self.callback_info    = None
        self.callback_warning = None
        self.callback_error   = None
        # Create a registry instance
        self.registry = Registry(self)
        # Create a store for directives
        self.directives = {}
        if register_prime: register_prime_directives(self)

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

    def add_file(self, path, ignore_duplicate=False):
        """ Add a file to the registry.

        Args:
            path            : Path to add
            ignore_duplicate: Don't raise an error if the file or folder already
                              exists in the registry (default: False)
        """
        self.registry.add_file(path, ignore_duplicate=ignore_duplicate)

    def add_folder(
        self,
        path,
        search_for      =None,
        recursive       =False,
        ignore_duplicate=False,
    ):
        """ Add a folder to the registry, see Registry.add_folder for more info.

        Args:
            path            : Path to the root folder to add
            search_for      : Provide a file extension to search for
            recursive       : Whether to search recursively in this folder
            ignore_duplicate: Don't raise an error if the file or folder already
                              exists in the registry (default: False)
        """
        self.registry.add_folder(
            path, search_for=search_for, recursive=recursive,
            ignore_duplicate=ignore_duplicate,
        )

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
            if tag.lower() in self.directives:
                raise PrologueError(f"Directive already registered for tag '{tag}'")
        # Register the directive
        for tag in dirx.tags: self.directives[tag.lower()] = dirx

    def deregister_directive(self, tag):
        """ Remove a previously registered directive.

        Args:
            tag: The tag of the directive
        """
        if tag.lower() not in self.directives:
            raise PrologueError(f"No directive registered for tag '{tag}'")
        for dirx_tag in self.directives[tag.lower()].tags:
            del self.directives[dirx_tag]

    def list_directives(self):
        """ Return all of the registered directives.

        Returns: A list of directives """
        return list(set(self.directives.values()))

    def has_directive(self, tag):
        """ Test if a directive has been registered for a given tag.

        Args:
            tag: The tag to check for

        Returns: True if the tag is known, False if not
        """
        return (tag.lower() in self.directives)

    def get_directive(self, tag):
        """
        Return a directive for a particular tag. If the delimiter is not shared
        and the tag isn't known, an error will be raised. If the delimiter is
        shared, then None will be returned.

        Args:
            tag: The tag of the directive

        Returns: Directive function if known, otherwise None
        """
        # Check if a directive exists for this tag
        if tag.lower() not in self.directives:
            if self.shared_delimiter:
                return None
            else:
                raise PrologueError(f"No directive known for tag '{tag}'")
        # Return the directive
        return self.directives[tag.lower()]

    # ==========================================================================
    # Evaluation
    # ==========================================================================

    def evaluate(
        self, filename, defines=None, callback=None, lookup=None, included=None,
    ):
        """ Iterable evaluation function which returns fully preprocessed stream

        Args:
            filename: The file to evaluate
            defines : Predefined values to initialise the context (default: None)
            callback: Optional callback provided to all directives to expose
                      state during parse to an external routine (default: None)
            lookup  : Optionally provide an empty list to capture lookup for
                      resolving output line to input line and file (default: None)
            included: Optionally provide an empty list to capture all files that
                      were included during preprocessing (default: None)

        Yields: Stream of fully preprocessed lines
        """
        # Create a context object used for tracking variables and parse state
        context = Context(
            self,
            implicit_sub  =self.implicit_sub,
            explicit_style=self.explicit_style,
            allow_redefine=self.allow_redefine,
            initial_state =defines,
        )
        # Use inner evaluation routine to get each line one at a time
        for line in self.evaluate_inner(filename, context, callback=callback):
            final = context.substitute(line)
            if isinstance(lookup, list): lookup.append((final.file, final.number))
            yield str(final)
        # Get all files included as part of the trace
        if isinstance(included, list): included += list(set(context.trace))

    def evaluate_inner(self, filename, context, callback=None):
        """
        Inner evaluation routine - this performs all construction and evaluation
        except variable substitution, which is performed by 'evaluate'.

        Args:
            filename: The file to evaluate
            context : A context object
            callback: Optional callback provided to all directives to expose
                      state during parse to an external routine (default: None)

        Yields: Stream of preprocessed lines, prior to substitution
        """
        # Find the top-level file
        r_file = self.registry.resolve(filename)
        if not r_file: raise PrologueError(f"Failed to find file {filename}")
        # Sanity check a context object was provided
        if not isinstance(context, Context):
            raise PrologueError(f"An invalid context was provided: {context}")
        # Stop infinite recursion by checking if this file is already in the stack
        if r_file in context.stack:
            raise PrologueError(
                f"Detected infinite recursion when including file '{filename}' "
                f"- file stack: {', '.join([x.filename for x in context.stack])}"
            )
        # Create regular expressions for recognising directives
        re_anchored = re.compile(
            r"^[\s]*[" + self.delimiter + r"]([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        re_floating = re.compile(
            r"^([^" + self.comment + "]*)[" + self.delimiter + r"]([a-z0-9_]+)(.*?)$", flags=re.IGNORECASE,
        )
        # Push the current file into the stack
        context.stack_push(r_file)
        # Start parsing
        active      = None
        accumulated = None
        for idx, line in enumerate(r_file.contents):
            # Catch any exceptions so that they can be marked with file and line
            try:
                # If comment and delimiter are different, remove everything after comment
                if self.comment != self.delimiter:
                    line = line.split(self.comment)[0]
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
                    if d_wrap and d_wrap.is_line:
                        l_dir = d_wrap.directive(
                            active, src_file=r_file, src_line=(idx + 1),
                            callback=callback,
                        )
                        l_dir.invoke(tag, arguments.strip())
                        if   active      : active.append(l_dir)
                        elif l_dir.yields: yield from l_dir.evaluate(context)
                        else             : l_dir.evaluate(context)
                        # Move on to the next line
                        continue
                    elif d_wrap and d_wrap.is_block:
                        # Call the directive
                        if d_wrap.is_opening(tag):
                            block   = d_wrap.directive(
                                active, src_file=r_file, src_line=(idx + 1),
                                callback=callback,
                            )
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
                        # Move on to the next line
                        continue
                # Test if the line matches a floating directive
                floating = re_floating.match(line)
                if floating != None:
                    prior, tag, arguments = floating.groups()
                    tag                   = tag.lower()
                    arguments             = arguments.strip()
                    d_wrap                = self.get_directive(tag)
                    if d_wrap and d_wrap.is_block:
                        raise PrologueError(
                            f"The directive '{tag}' can only be used with an "
                            f"anchored delimiter as it is a block directive"
                        )
                    elif d_wrap:
                        if arguments.endswith(":"): arguments = arguments[:-1]
                        # Yield the text before the directive
                        yield line.encase(prior.rstrip())
                        # Yield the contents returned from the directive
                        l_dir = d_wrap.directive(
                            active, src_file=r_file, src_line=(idx + 1),
                            callback=callback,
                        )
                        l_dir.invoke(tag, arguments.strip())
                        if   active      : active.append(l_dir)
                        elif l_dir.yields: yield from l_dir.evaluate(context)
                        else             : l_dir.evaluate(context)
                        continue
                # Otherwise, this is just a line!
                if active: active.append(line)
                else     : yield line
            # Catch all exceptions and add file and line
            except PrologueError as e:
                raise e
            except Exception as e:
                snippet = "\n".join(r_file.snippet(idx+1))
                raise PrologueError(
                    f"Caught {type(e).__name__} when evaluating {r_file.path}:"
                    f"{idx+1}; {e}" + "\n" + snippet
                ) from e
        # Check for trailing directives
        if active:
            dir_stack = [x for x in active.stack if isinstance(x, Directive)]
            src_file, src_line = active.source
            snippet = "\n".join(src_file.snippet(src_line))
            raise PrologueError(
                f"Unmatched {type(active).__name__} block directive in "
                f"{src_file.path}:{src_line}:" + "\n" + snippet
            )
        # Pop the file being parsed from the stack
        if context.stack_pop() != r_file:
            raise PrologueError("File stack has been corrupted")

    # ==========================================================================
    # Lookup
    # ==========================================================================

    def resolve(self, lookup, line, before=2, after=2):
        """
        Use the line lookup to resolve which input file and line number produced
        each line of the output.

        Args:
            lookup: A lookup list generated by Prologue during evaluation
            line  : Line number (from 1 to number of output lines, not an index)
            before: How many lines to include in the snippet before the target
            after : How many lines to include in the snippet after the target

        Returns: Tuple of input RegistryFile and the line number
        """
        # Sanity checks
        if not lookup or not isinstance(lookup, list):
            raise PrologueError(f"Lookup is either empty or not a list: {lookup}")
        elif not isinstance(line, int):
            raise PrologueError(f"Line number must be an integer - not '{line}'")
        elif line < 1 or line > len(lookup):
            raise PrologueError(
                f"Line {line} is out of valid range 1-{len(lookup)}"
            )
        # Use lookup to get the file and line number
        r_file, line_no = lookup[line-1]
        # Return the input file and line number
        return r_file, line_no, r_file.snippet(line_no, before, after)
