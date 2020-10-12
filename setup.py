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

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="prologue",
    version="0.1",
    license="Apache License, Version 2.0",
    description="Extensible block-based preprocessor written in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Peter Birch",
    url="https://github.com/Intuity",
    project_urls={
        "Source": "https://github.com/Intuity/prologue",
    },
    packages=["prologue"],
    data_files=["LICENSE"],
    include_package_data=True,
    entry_points={ },
    install_requires=[],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    extras_require={},
)
