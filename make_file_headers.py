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

@Description:
    Add headers to files with selected extensions automatically.
    The script will first list the files missing headers, then
    prompt for confirmation. The modification is made inplace.

    Usage:
        python3 make_file_headers.py <header file> <root dir>

    The script will first read the header template in <header file>,
    then scan for source files recursively from <root dir>.
"""

import sys
import os
import os.path as path
import fileinput
from typing import List


src_extensions: List[str] = ['.py', '.mplstyles']


def is_src_file(file: str) -> bool:
    """
    Check if a file's extension matches any of the specified source code extensions.

    This function takes a filename as input and checks if its extension matches any
    of the source code extensions defined in the global `src_extensions` list.

    :param file: File name (including extension) to be checked.
    :return: True if the file's extension is in `src_extensions`, False otherwise.
    """
    results = [file.endswith(ext) for ext in src_extensions]
    return True in results


def is_header_missing(file: str) -> bool:
    """
    Check if a file is missing a shebang line at the beginning.

    This function reads the contents of a file and checks if it begins with a shebang
    line (a line starting with "#!"). If the file is empty or doesn't start with a shebang,
    it is considered to have a missing header.

    :param file: File path to be checked.
    :return: True if the file is missing a shebang header, False otherwise.
    """
    with open(file) as reader:
        lines = reader.read().lstrip().splitlines()

        if len(lines) > 0:
            return not lines[0].startswith("#!")

        return True


def get_src_files(dirname: str) -> List[str]:
    """
    Find source code files in a directory and its subdirectories with missing headers.

    This function recursively searches for source code files (based on the file extensions
    specified in `src_extensions`) in the given directory and its subdirectories. It returns
    a list of file paths for source code files that have missing headers.

    :param dirname: Directory path to start the search.
    :return: List of file paths for source code files with missing headers.
    """
    src_files = []
    for cur, _dirs, files in os.walk(dirname):
        [src_files.append(path.join(cur, file)) for file in files if is_src_file(file)]

    return [file for file in src_files if is_header_missing(file)]


def add_headers(files_target: List[str], header_file: str) -> None:
    """
    Add headers to the specified files.

    This function takes a list of file paths and a header string and adds the header
    to the beginning of each file. It modifies the files in place.

    :param files_target: List of file paths to which the header will be added.
    :param header_file: Header content to be added to the files.
    :return: None
    """
    for line in fileinput.input(files_target, inplace=True):
        if fileinput.isfirstline():
            for h in header_file.splitlines():
                print(h)
        print(line, end="")


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]:s} <header file> <root dir>")
        exit()

    args = [path.abspath(arg) for arg in sys.argv]
    root_path = path.abspath(args[2])

    header = open(args[1]).read()
    files = get_src_files(root_path)

    print("Files with missing headers:")
    for f in files:
        print(f"\t- {f:s}")

    if len(files) == 0:
        print('\tNone found.')

    print("\nHeader:")
    print(header)

    confirm = input("proceed ? [Y/n] ")

    if confirm is not "Y":
        exit(0)

    add_headers(files, header)
