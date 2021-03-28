from contextlib import contextmanager
from os import chdir, getcwd


@contextmanager
def cd(destination: str) -> None:
    """
    A context manager to change directory. Mimics unix's cd.

    Args:
        destination (str): The directory to cd into.
    """
    cwd = getcwd()

    try:
        chdir(destination)
        yield
    finally:
        chdir(cwd)
