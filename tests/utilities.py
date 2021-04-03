from contextlib import contextmanager
from os import getcwd, chdir
from tempfile import TemporaryDirectory


@contextmanager
def tmpdir() -> None:
    """
    A context manager to go into a temporary directory.
    """
    with TemporaryDirectory() as temporary_directory:
        current_working_directory = getcwd()

        try:
            chdir(temporary_directory.name)
            yield
        finally:
            chdir(current_working_directory)
