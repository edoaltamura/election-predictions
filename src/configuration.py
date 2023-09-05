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
from dataclasses import dataclass, is_dataclass, field
from typing import List, Type, Callable, Any, TypeVar
import os.path
import pathlib

path_project = pathlib.Path(__file__).parent.parent.resolve()

T = TypeVar('T')


def nested_dataclass(*args: Any, **kwargs: Any) -> Callable[[Type[T]], Type[T]]:
    """
    A decorator to create nested dataclasses by automatically initializing nested objects from dictionaries.

    This decorator is applied to a class, and it checks if any class attributes have types that are also dataclasses.
    If so, it attempts to create instances of those nested dataclasses from dictionaries provided during object
    initialization.

    :param *args: Additional arguments (not used).
    :param **kwargs Additional keyword arguments (not used).

    :return: The decorated class.

    Example usage:
        ```python
        @nested_dataclass
        @dataclass
        class Address:
            street: str
            city: str
            postal_code: str

        @nested_dataclass
        @dataclass
        class Person:
            name: str
            age: int
            address: Address

        # Creating a Person object with a nested Address object from a dictionary
        person_data = {
            'name': 'John Doe',
            'age': 30,
            'address': {
                'street': '123 Main St',
                'city': 'Sampleville',
                'postal_code': '12345'
            }
        }
        person = Person(**person_data)
        ```
    """

    def wrapper(cls: Type[T]) -> Type[T]:
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self: T, *args: Any, **kwargs: Any) -> None:
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


@dataclass
class _DataConfigPaths:
    """
    Configuration class for data paths.

    This class defines paths for storing different types of data, such as raw, interim, and final data.
    """
    _base: str = os.path.join(path_project, 'data')
    _descriptions: List[str] = field(default_factory=lambda: ['raw', 'interim', 'final'])

    def __post_init__(self):
        """
        Initializes path attributes and checks for the existence of directories.
        """
        self.alloc_path_attributes()
        self.check_directories()

    def alloc_path_attributes(self):
        """
        Allocates path attributes based on descriptions.
        """
        for i, description in enumerate(self._descriptions):
            setattr(self, description, os.path.join(self._base, f"{i + 1:02d}_{description}"))

    def check_directories(self):
        """
        Checks if directories exist and creates them if necessary.
        """
        for description in self._descriptions:
            directory = getattr(self, description)
            if not os.path.isdir(directory):
                print(f'Creating data directory: {directory:s}')
                os.mkdir(directory)


@nested_dataclass(frozen=True)
class ConfigPaths:
    """
    Configuration class for project paths.

    This class defines paths for various project directories, such as reports, notebooks, mplstyles, and data.
    """
    reports: str = os.path.join(path_project, 'reports')
    notebooks: str = os.path.join(path_project, 'notebooks')
    mplstyles: str = os.path.join(path_project, 'src', 'mplstyles')
    data: _DataConfigPaths = _DataConfigPaths()

    def __repr__(self):
        """
        Returns a string representation of the instance.
        """
        return f'This is a {self.__class__.__name__} instance containing static paths to project directories.'


cfg_paths = ConfigPaths()
