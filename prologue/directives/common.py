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

from enum import IntEnum, auto

from .base import Directive, BlockDirective, LineDirective
from ..common import PrologueError

class DirectiveWrap(object):
    """ Decorator around a directive class or function """

    def __init__(self, dirx, opening, closing=None, transition=None):
        """ Initialise the wrapper

        Args:
            dirx      : The directive class or function
            dir_type  : Type of the directive (e.g. BLOCK or LINE)
            opening   : List of opening tags for the directive
            closing   : List of closing tags for the directive (only used for block)
            transition: Optional list of tags which transition between sections
        """
        # Store and check directive
        self.directive = dirx
        if not issubclass(dirx, Directive):
            raise PrologueError(f"Item is not a subclass of Directive: {dirx}")
        # Force tags to be case insensitive
        if opening   : opening    = [x.lower() for x in opening   ]
        if closing   : closing    = [x.lower() for x in closing   ]
        if transition: transition = [x.lower() for x in transition]
        # Check tags
        opening    = tuple(opening) if isinstance(opening, list) else opening
        closing    = tuple(closing) if isinstance(closing, list) else closing
        transition = tuple(transition) if isinstance(transition, list) else transition
        if not isinstance(opening, tuple) or len(opening) == 0:
            raise PrologueError("At least one opening tag must be specified")
        if self.is_block and (not isinstance(closing, tuple) or len(closing) == 0):
            raise PrologueError("At least one closing tag must be specified")
        elif not self.is_block and closing != None:
            raise PrologueError("Only a block directive can have closing tags")
        elif not self.is_block and transition != None:
            raise PrologueError("Only a block directive can have transition tags")
        for tag in (
            opening +
            (closing if closing else tuple()) +
            (transition if transition else tuple())
        ):
            if " " in tag or len(tag) == 0:
                raise PrologueError(
                    "Directive tag cannot contain spaces and must be at least "
                    "one character in length"
                )
        # Store arguments
        self.opening    = opening
        self.closing    = closing if closing else tuple()
        self.transition = transition if transition else tuple()

    @property
    def tags(self):
        """ Return all tags - opening and closing """
        return (self.opening + self.transition + self.closing)

    @property
    def is_block(self):
        """ Returns if this is a block directive """
        return (
            isinstance(self.directive, type) and
            issubclass(self.directive, BlockDirective)
        )

    @property
    def is_line(self):
        """ Returns if this is a line directive """
        return (
            isinstance(self.directive, type) and
            issubclass(self.directive, LineDirective)
        )

    def is_opening(self, tag):
        """ Test if a particular tag is an opening tag.

        Args:
            tag: The tag to test

        Returns: True if this is an opening tag, False otherwise
        """
        if   tag in self.opening: return True
        elif tag in (self.closing + self.transition): return False
        else: raise PrologueError(f"Tag is not known by directive: {tag}")

    def is_transition(self, tag):
        """ Test if a particular tag is a transition tag.

        Args:
            tag: The tag to test

        Returns: True if this is a transition tag, False otherwise
        """
        if   tag in self.transition: return True
        elif tag in (self.opening + self.closing): return False
        else: raise PrologueError(f"Tag is not known by directive: {tag}")

    def is_closing(self, tag):
        """ Test if a particular tag is a closing tag.

        Args:
            tag: The tag to test

        Returns: True if this is a closing tag, False otherwise
        """
        if   tag in self.closing: return True
        elif tag in (self.opening + self.transition): return False
        else: raise PrologueError(f"Tag is not known by directive: {tag}")

def directive(*tags, opening=None, closing=None, transition=None):
    """ Decorator for a block directive

    Args:
        *tags     : List of tags identifying directive (alias of opening)
        opening   : Tags that open a block directive
        closing   : Tags that close a block directive
        transition: Tags that transition between sections of the block
    """
    # Pickup tags list if explicit opening list not provided
    if not opening: opening = []
    opening += tags
    # Force tags to lowercase
    opening = [x.lower() for x in opening]
    if transition: transition = [x.lower() for x in transition]
    if closing   : closing    = [x.lower() for x in closing   ]
    # Setup the wrapper function
    def wrapper(_dirx):
        if not opening:
            raise PrologueError(
                "At least one opening directive must be given"
            )
        if not issubclass(_dirx, BlockDirective) and not issubclass(_dirx, LineDirective):
            raise PrologueError(
                "Directive must be a subclass of BlockDirective or LineDirective"
            )
        elif issubclass(_dirx, LineDirective) and (closing or transition):
            raise PrologueError(
                "Closing or transition tags can only be used with a block directive"
            )
        elif issubclass(_dirx, BlockDirective) and not closing:
            raise PrologueError(
                "Closing tags must be specified for a block directive"
            )
        # Record tags against the registered class
        _dirx.OPENING    = opening
        _dirx.TRANSITION = transition
        _dirx.CLOSING    = closing
        # Return the wrapped directive
        return DirectiveWrap(_dirx, opening, closing, transition)
    return wrapper
