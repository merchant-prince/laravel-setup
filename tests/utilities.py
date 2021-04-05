from contextlib import contextmanager
from os import getcwd, chdir
from tempfile import TemporaryDirectory


@contextmanager
def tmpdir() -> None:
    """
    A context manager to create a temporary directory and cd into it.
    """
    current_working_directory = getcwd()

    with TemporaryDirectory() as temporary_directory:
        try:
            chdir(temporary_directory)
            yield
        finally:
            chdir(current_working_directory)
