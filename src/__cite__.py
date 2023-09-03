#!/usr/bin/env python
# encoding: utf-8

"""
@Author:              Edoardo Altamura
@Year:                2023
@Email:               edoardo.altamura@outlook.com
@Copyright:           Copyright (c) 2023 Edoardo Altamura
@Last Modified by:    Edoardo Altamura
@Latest release:      5 Sep 2023
@Project:             Election predictions (Data Science with The Economist)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import warnings
import datetime
import os.path

from .configuration import path_project
# Fetch the date of last commit from the parent directory. Initialise to the creation date.
__date_last_update__ = '2023-08-25'

try:
    import git

    repo = git.Repo(path_project)
    tree = repo.tree()
    for blob in tree:
        commit = next(repo.iter_commits(paths=blob.path, max_count=1))
        timestamp = commit.committed_date
        __date_last_update__ = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

except ModuleNotFoundError:
    warnings.warn('Git-python module was not found, but you can install it with <pip install GitPython>. Returning '
                  'the date of creation.',
                  UserWarning)

except:
    warnings.warn('Could not retrieve the date of last commit. Returning the date of creation.',
                  UserWarning)

# Fetch the version from the base file
with open(os.path.join(path_project, "src", "__version__.py"), "r") as fh:
    exec_output = {}
    exec(fh.read(), exec_output)
    __version__ = exec_output["__version__"]

# Check the str format of the variables
assert isinstance(__version__, str)
assert isinstance(__date_last_update__, str)

# Build citation handle for bibtex
__cite__ = (r"@software{altamura_elections," "\n"
            r"  author = {{Altamura}, Edoardo}," "\n"
            r'  title = {"An statistical machine learning framework for election predictions"},' "\n"
            r"  url = {https://github.com/edoaltamura/election-predictions}," "\n"
            f"  version = {{{__version__:s}}}," "\n"
            f"  date = {{{__date_last_update__:s}}}," "\n"
            r"}")
