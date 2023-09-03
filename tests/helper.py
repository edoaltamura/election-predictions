"""
Contains helper functions for the test routines.
"""

import subprocess
import os
from typing import Callable, Any

webstorage_location: str = "http://<remote:database>/"
test_data_location: str = "test_data/"


def requires(filename: str) -> Callable:
    """
    Use this as a decorator around tests that require data.
    """

    # First check if the test data directory exists
    if not os.path.exists(test_data_location):
        os.mkdir(test_data_location)

    file_location = f"{test_data_location}{filename}"

    if os.path.exists(file_location):
        ret = 0
    else:
        # Download it!
        ret = subprocess.call(
            ["wget", f"{webstorage_location}{filename}", "-O", file_location]
        )

    if ret != 0:
        Warning(f"Unable to download file at {filename}")

        # It wrote an empty file, kill it.
        subprocess.call(["rm", file_location])

        def dont_call_test(func: Callable) -> Callable:

            def empty(*args, **kwargs) -> bool:
                return True

            return empty

        return dont_call_test

    else:

        def do_call_test(func: Callable) -> Callable:

            def final_test() -> Any:
                # Return the path on there for good measure
                return func(f"{test_data_location}{filename}")

            return final_test

        return do_call_test
