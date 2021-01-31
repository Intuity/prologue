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
import shlex

import asteval

from .common import PrologueError, Line
from .registry import RegistryFile

class Context(object):
    """ Keeps track of the parser's context """

    def __init__(
        self, pro, parent=None, implicit_sub=True, explicit_style=("$(", ")"),
    ):
        """ Initialise the context

        Args:
            pro           : Pointer to the root Prologue instance
            parent        : Pointer to the parent Context object prior to fork
            implicit_sub  : Whether to allow implicit substitutions (default: True)
            explicit_style: Tuple of strings that define the explicit style
                            (default: ('$(', ')'))
        """
        self.pro            = pro
        self.parent         = parent
        self.implicit_sub   = implicit_sub
        self.explicit_style = explicit_style
        self.__defines      = {}
        self.ast_eval       = asteval.Interpreter()
        self.__stack        = []
        self.__trace        = []
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

    def set_define(self, key, value, warning=True):
        """ Define a value for a key, checks whether the key clashes.

        Args:
            key    : The key of the define
            value  : The value of the define
            warning: Warn about redefining an existing variable
        """
        # Check the key is sane
        if " " in key or len(key) == 0:
            raise PrologueError(
                f"Key must not contain whitespace and must be at least one "
                f"character in length: '{key}'"
            )
        # Warn about collision
        if warning and key in self.defines:
            self.pro.warning_message(
                f"Value already defined for key {key}",
                { "key": key, "value": value },
            )
        # Store the define
        self.__defines[key] = value

    def clear_define(self, key):
        """
        Remove a defined value from the context based on a key, an exception is
        raised if the key is unknown.

        Args:
            key: The key of the defined value
        """
        if key not in self.defines:
            raise PrologueError(f"No value has been defined for key '{key}'")
        del self.__defines[key]

    def has_define(self, key):
        """ Check if a variable has been defined.

        Args:
            key: The key of the defined value

        Returns: True if defined, False otherwise
        """
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
        if key not in self.__defines:
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
        for key, value in self.__defines.items():
            self.parent.set_define(key, value)
        return self.parent

    # ==========================================================================
    # Expression Evaluation
    # ==========================================================================

    def flatten(self, expr, skip_undef=False):
        """ Flatten an expression by substituting for known variables.

        Args:
            expr      : The expression to flatten
            skip_undef: Skip undefined variables (instead of erroring)

        Returns: String with each recognised variable substituted for its value
        """
        # Pickup candidates for substitution
        rgx_const = re.compile(r"\b([a-z][a-z0-9_]*)\b", re.IGNORECASE)
        matches   = [x for x in rgx_const.finditer(expr)]
        # If no candidates detected, break out early
        if len(matches) == 0: return str(expr)
        # Substitute for each variable
        final = ""
        for idx, match in enumerate(matches):
            var_name = match.groups(0)[0]
            if not self.has_define(var_name):
                if skip_undef:
                    final += (
                        expr[matches[idx-1].span()[1]:match.span()[1]] if idx > 0 else
                        expr[:match.span()[1]]
                    )
                    continue
                else:
                    raise PrologueError(f"Referenced unknown variable '{var_name}'")
            # Pickup the section that comes before the match
            final += (
                expr[matches[idx-1].span()[1]:match.span()[0]] if idx > 0 else
                expr[:match.span()[0]]
            )
            # Make the substitution
            value = self.get_define(var_name)
            if isinstance(value, str):
                final += self.flatten(value, skip_undef=skip_undef)
            else:
                final += str(value)
        # Catch the trailing section
        final += expr[matches[-1].span()[1]:]
        # Return concatenated string
        return final

    def evaluate(self, expr, skip_undef=False):
        """ Flatten an expression, then evaluate it.

        Args:
            expr      : The expression to evaluate
            skip_undef: Skip undefined variables (instead of erroring)

        Returns: Result of the expression
        """
        # First flatten out variable references
        flat = self.flatten(expr.strip(), skip_undef=skip_undef)
        # Now evaluate (if we can)
        result = self.ast_eval(flat)
        if self.ast_eval.error:
            self.ast_eval.error = []
            return flat
        else:
            return result

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
            sub_val = self.evaluate(m_expr, skip_undef=True)
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
                        str(self.get_define(match.groups()[0])) +
                        line[match.span()[1]:]
                    )
        # Return the finished string
        return Line(line, f_file, f_line)
