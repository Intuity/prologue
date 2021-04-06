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

import ast
import re
import shlex
import sys

# Support AST unparsing across multiple Python versions
# NOTE: Before Python 3.9, unparse was not a native function
if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse

from .common import PrologueError, Line
from .registry import RegistryFile

class Context(object):
    """ Keeps track of the parser's context """

    def __init__(
        self,
        pro,
        parent        =None,
        implicit_sub  =True,
        explicit_style=("$(", ")"),
        allow_redefine=False,
        initial_state =None,
    ):
        """ Initialise the context

        Args:
            pro           : Pointer to the root Prologue instance
            parent        : Pointer to the parent Context object prior to fork
            implicit_sub  : Whether to allow implicit substitutions (default: True)
            explicit_style: Tuple of strings that define the explicit style
                            (default: ('$(', ')'))
            allow_redefine: Allow values to be defined multiple times (default:
                            False, so a PrologueError will be raised on redefine)
            initial_state : Dictionary of values to provide an initial state
                            (default: None)
        """
        self.pro            = pro
        self.parent         = parent
        self.implicit_sub   = implicit_sub
        self.explicit_style = explicit_style
        self.allow_redefine = allow_redefine
        self.__defines      = {}
        self.__removed      = []
        self.__stack        = []
        self.__trace        = []
        # Populate initial state
        if isinstance(initial_state, dict):
            for key, value in initial_state.items():
                if not isinstance(key, str):
                    raise PrologueError(
                        f"Keys must be strings in initial state, not: {key}"
                    )
                elif type(value) not in (str, int, float, bool):
                    raise PrologueError(
                        f"Values must be string, integer, float, or Boolean in "
                        f"the initial state, not: {value}"
                    )
                self.__defines[key] = value
        elif initial_state != None:
            raise PrologueError(
                f"Initial state must be a dictionary, not: {initial_state}"
            )
        # Define regular expression for variable substitution
        rgx_exp_str = r"(" + "".join(f"[{x}]" for x in self.explicit_style[0])
        if explicit_style[1]:
            rgx_exp_str += r".*?"
            rgx_exp_str += "".join(f"[{x}]" for x in self.explicit_style[1])
        else:
            rgx_exp_str += r"[a-z_][a-z0-9_]+"
        rgx_exp_str += r")"
        self.rgx_exp = re.compile(rgx_exp_str, flags=re.IGNORECASE)
        self.rgx_imp = re.compile(r"\b([a-z][a-z0-9_]{0,})\b", flags=re.IGNORECASE)

    @property
    def defines(self):
        """ Returns all defines across the full stack of context objects """
        return {
            **(self.parent.defines if self.parent else {}), **self.__defines
        }

    @property
    def root(self):
        """ Returns the root context object """
        return self.parent.root if self.parent else self

    @property
    def stack(self):
        """ Returns the root file stack object """
        return self.root.stack if self.parent else self.__stack

    @property
    def trace(self):
        """ Returns the root file trace object """
        return self.root.trace if self.parent else self.__trace

    # ==========================================================================
    # File Stack Management
    # ==========================================================================

    def stack_push(self, file):
        """ Push a new file onto the stack.

        Args:
            file: Instance of RegistryFile to push
        """
        # Sanity check this is the correct type
        if not isinstance(file, RegistryFile):
            raise PrologueError(
                f"Trying to push {file} to stack - must be a RegistryFile"
            )
        # Push to stack
        self.stack.append(file)
        # Also push file to the trace - it records order files were read
        self.trace.append(file)

    def stack_pop(self):
        """ Pop a file from the stack.

        Returns: Next instance of RegistryFile from the top of the stack.
        """
        # Sanity check
        if len(self.stack) == 0:
            raise PrologueError("Trying to pop file from empty stack")
        # Pop the top entry off the stack
        return self.stack.pop()

    def stack_top(self):
        """ Get the top RegistryFile instance from the stack (if any exist).

        Returns: RegistryFile instance if stack populated, else None.
        """
        # Return the top item off the stack
        return self.stack[-1] if len(self.stack) > 0 else None

    # ==========================================================================
    # Defined Constant Handling
    # ==========================================================================

    def set_define(self, key, value, check=True):
        """ Define a value for a key, checks whether the key clashes.

        Args:
            key  : The key of the define
            value: The value of the define
            check: Check whether an existing variable is about to be redefined
        """
        # Check the key is sane
        if " " in key or len(key) == 0:
            raise PrologueError(
                f"Key must not contain whitespace and must be at least one "
                f"character in length: '{key}'"
            )
        # Warn about collision
        if check:
            if key in self.defines and not key in self.__removed:
                msg = (
                    f"Value already defined for key '{key}' with value "
                    f"{self.get_define(key)}"
                )
                if self.allow_redefine:
                    self.pro.warning_message(msg, key=key, value=value)
                else:
                    raise PrologueError(msg)
        # If the value is a number, convert it
        if isinstance(value, str) and value.strip().isdigit(): value = int(value)
        # Store the define
        self.__defines[key] = value
        # Clear define name from 'removed' array, if present
        if key in self.__removed: self.__removed.remove(key)

    def clear_define(self, key):
        """
        Remove a defined value from the context based on a key, an exception is
        raised if the key is unknown.

        Args:
            key: The key of the defined value
        """
        if key not in self.defines:
            raise PrologueError(f"No value has been defined for key '{key}'")
        if key in self.__defines:
            del self.__defines[key]
        else:
            self.__removed.append(key)

    def has_define(self, key):
        """ Check if a variable has been defined.

        Args:
            key: The key of the defined value

        Returns: True if defined, False otherwise
        """
        # If removed at this level, immediately return False
        if key in self.__removed: return False
        # If defined at this level, immediately return True
        if key in self.__defines: return True
        # Check if defined by my parent instead?
        if self.parent: return self.parent.has_define(key)
        # Otherwise, it's not defined!
        return False

    def get_define(self, key):
        """ Return a value if the key is known, otherwise raise an exception.

        Args:
            key: The key of the defined value

        Returns: Value of the define
        """
        if key in self.__removed:
            raise PrologueError(f"No value has been defined for key '{key}'")
        elif key not in self.__defines:
            if self.parent:
                return self.parent.get_define(key)
            else:
                raise PrologueError(f"No value has been defined for key '{key}'")
        return self.defines[key]

    # ==========================================================================
    # Forking and Joining
    # ==========================================================================

    def fork(self):
        """
        Creates a new context object with tracking of parent instance. This
        allows variable state to propagate from the parent, but be overridden
        locally - which is vital in supporting nested block evaluation.

        Returns: Instance of Context
        """
        return Context(self.pro, parent=self, implicit_sub=self.implicit_sub)

    def join(self):
        """ Joins a child context object back into it's parent.

        Returns: Pointer to the parent context
        """
        if not self.parent:
            raise PrologueError("No parent configured for context object")
        for key in self.__removed:
            self.parent.clear_define(key)
        for key, value in self.__defines.items():
            self.parent.set_define(key, value, check=False)
        return self.parent

    # ==========================================================================
    # Expression Evaluation
    # ==========================================================================

    def flatten(self, expr, history=None):
        """ Flatten an expression by substituting for known variables.

        Args:
            expr   : The expression to flatten
            history: Tracks expressions to avoid deadlock

        Returns: String with each recognised variable substituted for its value
        """
        # Create a history if one doesn't already exist
        if not history: history = []
        history.append(expr)
        # Declare a AST node transformation to replace variables
        ctx      = self
        replaced = [0]
        class ReplaceVar(ast.NodeTransformer):
            def visit_Name(self, node):
                if ctx.has_define(node.id):
                    replaced[0] += 1
                    value = ctx.get_define(node.id)
                    if not isinstance(value, str):
                        return ast.Constant(value=value, kind=type(value))
                    else:
                        return ast.parse(value).body[0]
                else:
                    return ast.Constant(value=node.id, kind=type(node.id))
        # Iterate repeating variables (constants may reference other constants)
        result = expr
        while True:
            # If result is no longer a string, break out
            if not isinstance(result, str): break
            # If it's not a constant, then try to substitute
            replaced[0] = 0
            try:
                # Walk the AST substituting variables -> constants
                result = unparse(ReplaceVar().visit(ast.parse(result)))
            except TypeError:
                break
            if replaced[0] == 0: break
        return result

    def evaluate(self, expr):
        """ Flatten an expression, then evaluate it.

        Args:
            expr: The expression to evaluate

        Returns: Result of the expression
        """
        # First flatten out variable references
        flat = self.flatten(expr.strip())
        # Now evaluate (if we can)
        try:
            return eval(flat, { "__builtins__": None }, { })
        except Exception:
            return flat

    def substitute(self, line, implicit=None):
        """ Perform in-line substitutions for recognised variables.

        Args:
            line    : The line to perform substitution on
            implicit: Enable implicit substitutions

        Returns: Line with values substituted
        """
        # If implicit not given, then it defaults to instance version
        if implicit == None: implicit = self.implicit_sub
        # Pickup the input line's attributes
        f_file, f_line, line = line.file, line.number, str(line)
        # First look for explicit substitutions of the form '$(x)'
        exp_match = [x for x in self.rgx_exp.finditer(line)]
        final     = ""
        exp_match = [x for x in self.rgx_exp.finditer(line)]
        for match in exp_match[::-1]:
            m_expr  = match.groups()[0][
                len(self.explicit_style[0]):
                len(match.groups()[0])-len(self.explicit_style[1])
            ]
            sub_val = self.evaluate(m_expr)
            line    = (
                line[:match.span()[0]] + str(sub_val) + line[match.span()[1]:]
            )
        # Secondly look for implicit substitutions
        if implicit:
            imp_match = [x for x in self.rgx_imp.finditer(line)]
            # Substitute each identified variable
            for match in imp_match[::-1]:
                if self.has_define(match.groups()[0]):
                    line = (
                        line[:match.span()[0]] +
                        str(self.evaluate(match.groups()[0])) +
                        line[match.span()[1]:]
                    )
        # Return the finished string
        return Line(line, f_file, f_line)
