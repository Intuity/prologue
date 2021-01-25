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

class PrologueError(Exception):
    """ Custom exception class - raised when Prologue detects processing errors """
    pass

class Line(str):
    """ Carries a line from a file, along with the line number and file pointer """

    def __new__(cls, line, file, number):
        return super().__new__(cls, line)

    def __init__(self, line, file, number):
        """ Initialise the line object.

        Args:
            line  : The string representing the line
            file  : Pointer to the file that contains this line
            number: The line number (minimum value of 1) within the file
        """
        super().__init__()
        assert isinstance(number, int) and number >= 1
        self.file   = file
        self.number = number

    def __repr__(self):
        return f"{self.file}@{self.number}: {self.__str__()}"

    def encase(self, substring):
        """ Encase a substring with the same file pointer and line number.

        Args:
            substring: The substring to encase
        """
        return Line(str(substring), self.file, self.number)

    def __getitem__(self, item):
        """ Custom handler for accessing single character or range in a line.

        Args:
            item: Character index or range to retrieve
        """
        return self.encase(super().__getitem__(item))

    def split(self, *args, **kwargs):
        return [self.encase(x) for x in super().split(*args, **kwargs)]

    def strip(self, *args, **kwargs):
        return self.encase(super().strip(*args, **kwargs))

    def __add__(self, other):
        return self.encase(super().__add__(other))
